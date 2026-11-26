# The browser read of 26 November 2026: everything landed since 20 November, and what lands tonight

Energy Research Warehouse (ERW). Chain 750 (`queue/done/750-night-26-november-portable-window2-browser-read.md`), the portable laptop's second window, sessions 11000 on. Every page is read on production (`https://erw-flame.vercel.app`) in the internal view, in the laptop's own Chrome driven by `site/scripts/browser.mjs`, at 1280 px with a mouse and at 390 px with a finger (touch events). No build is made here and no model is called. The scripts are in `runs/c750/` on the laptop (not in git); the pictures are in `docs/reviews/browser-read-2026-11-26/`.

How a row reads: what was done, what was seen, what should be seen, and whose it is. A site fault on a page no window owns tonight is fixed on a branch `wip/c750-<page>` with a test and is a row of `docs/state/landing_request_portable_w2.md`. A fault on a page another window owns tonight is a row here that names the window, and its code is not edited. A data fault is a row of `docs/state/data_requests_done_line.md`. A thing that is a choice is one line under "For Samuel's ruling" at the foot, with the page left as it is.

## Part A: the rows that waited for a browser

Rows 418 to 422 of `docs/state/browser_reads_wanted.md` were the only rows in state `wanted`. On 20 November their commits (the old laptop's sessions 8470, 8480 and 8490) were not in main. All three branch heads are in main now (`c7a96eea1`, `34c53f280`, `1e3a9e95b`), so each was read on production at 1280 and 390 px on 26 November about 11:20 UTC. All five are marked `seen` there, with the words read.

| Row | Address | What was seen | State |
|---:|---|---|---|
| 418 | `/events/uri-2021?region=tex&b=cent#whole-country`, and `/events/caiso-heat-2020?region=nw&b=cal#whole-country` | The Midwest's net imports hover gives both figures (pairs +9,619 MW against net imports +5,427 MW over 435 hours) and why they need not agree. Over Uri the Northwest's sources now rest on 434 hours both sides hold, so the line the row asked for was read where the case still arises, the Northwest over the August 2020 heat: "Northwest's sources are held for no hour of the window and 123 of the baseline, never the same hour, so none is set against it". No sideways scroll | seen |
| 419 | `/demand?view=country&a=se&b=fla&figure=summer&year=2025` | Each of the nine blank weather cells says why it is blank, with the 95 percent rule and the regions' 80 to 99 percent of hours; "no growth since 2019" has its hover; the long names fit; no sideways scroll | seen |
| 420 | `/demand?view=country&a=ba-miso&b=ba-lgee` | MISO's newest day (now 19 November 2026) is blank with the hover "23 of the day's 24 hours are used, so no demand of the whole day is given"; twelve charts drawn | seen |
| 421 | `/supply?region=mida&b=midw&year=2022#whole-country` and `year=2021` | 2025 now holds every month, so the row was read on the Mid-Atlantic's June 2022 and the Midwest's March 2021: each is a row reading "not held yet" with the builder's 90 percent rule on hover; no sideways scroll of the page | seen |
| 422 | `/supply?region=ten&b=car&year=2025#whole-country` | The mean's hover says it runs over the 8,734 hours both reported and need not lie between the two reports; the percent's hover says the two sides filed different hours (8,759 and 8,735) | seen |

Pictures: `docs/reviews/browser-read-2026-11-26/part-a/row418-caiso-heat-2020-northwest-line-1280.png` (the line under the sources table naming the Northwest, with its row of blanks above); `docs/reviews/browser-read-2026-11-26/part-a/row421-supply-midatlantic-june-2022-390.png` (the mix table at 390 px with June 2022 as a row of "not held yet").

Two things these reads showed beside what the rows asked, carried into part B's sections:

1. **A reason given on hover cannot be opened by a finger.** Every reason read above (why a cell is blank, why two figures differ) is the browser's own tooltip (a `title`). At 390 px with touch a tap opens none of them. The "i" marks and the chart cards do open on a tap; a blank cell's reason does not. Not new (chain 620 noted it for three charts as row S2), and it is site-wide, so it is one line under "For Samuel's ruling" and not a fix here.
2. **The mix table grows by half when a month is left out** (`/supply`, whole country): the words "not held yet" do not wrap, so the table is 1,325 px wide inside its 358 px frame at 390 px (900 px for a year with every month), and two columns show at a time. The page itself stays 390 px wide. Row S1 of the `/supply` section below.

## Part B: the list (written 26 November about 11:45 UTC, from main at `7c4001dc2`)

Where it comes from: the notes and progress files of chains 601, 610, 620 and 630, the five landing files, and main's log since 20 November. The last commit that changed a page's code reached main on 21 November at 04:06 UTC (`f3de295fa`); from then to tonight main took only the GitHub daily run's files. So the list is the landings of 20 and 21 November, and each line says whether a browser read it on production after it landed.

Two things found while writing the list, before any page was opened:

- **L1. Two fixes read "landed" and are not on main.** Row 4 of `docs/state/landing_request_window2.md` (`wip/w2-c620-fixes`) reads landed at `0fc82399d` (21 November 00:10 UTC). The desk landed the head `1d7b451a6`; the row's head was moved to `923d4cb4f` at 01:05 UTC, after the landing, and its state stayed landed. Two commits never reached main: `4f3247287` (`/curtailment/where-when`: the trend's table names the fuel it sums) and `923d4cb4f` (`/events/covid-2020` keeps to 390 px with a chart switched to its table), each with its test. The branch merges with today's main without a conflict (`git merge-tree`). The same slip as the old laptop's rows 51 to 53 on 19 November. Every other landed branch of 20 and 21 November was checked the same way (fourteen branch tips): each is in main whole. Both faults are read on production below (B10), and the two commits are a row of `docs/state/landing_request_portable_w2.md`.
- **L2. The page files a reader sees are those of 20 and 21 November.** The data machine's daily commit of page files went to `wip/red-dm-2026-11-21` to `wip/red-dm-2026-11-25` each day (its push is refused when the suite fails on the commit), so main, and production, hold the region files built 21 November 01:08 UTC, the conditions, states, storage and seller files built 20 November, and so on (`runs/c750/b_fresh.py`). The branch of 25 November changes 485 site files against main. This is known and is window A's tonight (chain 701, part C, item 3), so no request is filed; the reads below say which day each page shows, and the pages are read again when the repair lands.

| # | Page or view | Address | Built by | Landed (UTC) | A browser on production since? |
|---:|---|---|---|---|---|
| B1 | The policy week grid: each button named, a zero at full strength | `/policy?view=week` | desktop window 3 (chain 610, part D), without a browser | 21 Nov 02:05 | no |
| B2 | The severance calculator: the credit's tier list named | `/severance` | desktop window 3 | 21 Nov 02:05 | no |
| B3 | One h1 a page and no level skipped | `/data/licenses`, `/map?tab=resources`, `/map?tab=queues` | desktop window 3 | 21 Nov 02:05 | no |
| B4 | The Grid tool's reliability table: a year with no days | `/grid` | desktop window 3 | 21 Nov 02:05 | no |
| B5 | The findings review page's charts | `/internal/findings` | desktop window 4 (row 8) | 21 Nov 02:05 | no |
| B6 | Grid conditions with two operators at a phone's width (row H4), and the page in full | `/conditions` | data machine (chain 601) | 20 Nov 13:43; H4 on 21 Nov 00:10 | figures and quiet faults on 20 Nov (chain 620); not since H4, and not by hand |
| B7 | The thirteen regions in the Grid tool on the files rebuilt 21 November | `/grid?region=<region>` | data machine | 21 Nov 03:15 | no |
| B8 | The problem edition of 21 November | `/problems` and its sets | data machine | 21 Nov 04:06 | no |
| B9 | Chain 620's ten fixes and the tour's eighth stop | the back button on lists, `/internal/findings`, the resource set, the Grid panel's words, the tour, the price map's window, `/policy`, `/map` lines, the method pages, `/data/faults` | portable laptop (chain 620), seen in a build by desktop window 2 | 21 Nov 00:10 | no (seen in a build only) |
| B10 | The two fixes of L1 | `/curtailment/where-when`, `/events/covid-2020` | desktop window 2 | not landed | the faults read on production |
| B11 | Where the grid is congested, in full | `/congestion` | data machine (chain 601) | 20 Nov 13:43; rows H1, H2 at 16:32; traced at 17:48 | figures against its file three times on 20 Nov (chain 620); not by hand |
| B12 | The events, demand and supply pages on the real region files (the old laptop's rows 51 to 53) | `/events/<event>#whole-country`, `/demand?view=country`, `/supply#whole-country` | old laptop | 21 Nov 00:10 | read in full before the landing (desktop window 2); part A above read five rows after it |
| B13 | The variables table on the method pages | `/data/methods/<note>` | desktop window 2 (chain 630); window B's tonight (chain 730): read, never edited | 20 Nov 16:32 | 473 pages cell for cell on 20 Nov (chain 620) |
| B14 | The five pages the reader-page tests cover (tests only, no page change) | `/ai-energy`, `/industry`, `/queues/places`, `/storage/places`, `/curtailment/where-when` | desktop window 3 | 21 Nov 02:05 | read in full on 20 Nov (chain 620), before |

The pages no browser has seen come first: B1 to B5, then B6 to B10, then the rest. Tonight's pages (`/forecast`, `/equities`, the board's new group, `/impact` with Datacenter, the All grids tab) are part C, read as each lands.
