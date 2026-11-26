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

## The first pass and the sweep (26 November, 11:28 to 11:40 UTC)

- **Twelve addresses of the list at both widths** (`runs/c750/survey.mjs`): every page loads in under 3.3 s but `/internal/findings` (4.7 s at 1280 px, 3.5 s at 390 px); no sideways scroll, no empty chart, no heading that skips a level, no error in the console as each opens. `/problems` is no address (the sets live under `/learn`; B8 reads them there).
- **Every page with a fixed address (82) and the Grid tool's 63 views (eight grids and thirteen regions, three views each), at 390 px** (`runs/c750/all_routes.mjs`, 146 addresses, 11:35 UTC). With something wrong: `/grid?grid=caiso` (row G1 below); `/data/licenses` shows the word "undefined" inside an address (row D1 below: the publisher's own answer, settled on 20 November, not a fault); `/cost-of-power` took 5.3 s and `/internal/waits` 8.4 s to load. `/data/standard` prints "null" as a word of its own text ("No sentinel codes (-999, NA, null)"), which is right.

## B4 and row G1: the Grid tool's reliability table (`/grid?grid=caiso#reliability`)

Whose: no window's page tonight (the old laptop's Grid audit, chain 710 part D, is of the tool's figures). Read on production at 1280 and 390 px (`runs/c750/b_a11y2.mjs`, `runs/c750/b4_cause.mjs`).

- **The fix of 20 November is there.** The table "Every notice since 1998: days per year" has 226 cells with no day; each shows a dot in the muted text color (rgb 107, 103, 95 on white: 5.6 to 1) and is read aloud as "none". At 1280 px the page is 1265 of 1265 px wide.
- **G1, a fault the fix brought with it: at 390 px the page is 539 px wide.** Done: `/grid?grid=caiso` opened at 390 px. Seen: the page scrolls sideways to 539 px (the header, the text and every chart slide off to the left). Should be seen: 390 px, the table scrolling inside its own frame, as on 20 November. Cause, shown on production's own page: each "none" label is placed "absolute" (the class `sr-only`); the table's frame scrolls sideways but is not the labels' containing block, so it does not clip them, and the 60 labels of the columns past the frame's right edge (to 538 px) widen the whole page. With the labels hidden the page is 390 px wide; with the labels back and the frame made "relative", 390 px, the table still 526 px wide inside its 358 px frame and the cells still read "none". The session that added the labels had no browser, and the last phone sweep (20 November) was a day before they landed.
- **Fixed** on `wip/c750-grid-reliability` (`038ecbfcd`): the frame is `relative`; `tests/test_session11000_grid_reliability_phone.py` holds the rule for this component and fails on the code before. Row 1 of `docs/state/landing_request_portable_w2.md`, ready, to be seen. The other 145 addresses of the sweep keep to 390 px, so no other page has this today; 38 other components use `sr-only`, and the same thing would happen in any of them the day a label lands inside a wide table.

Pictures: `docs/reviews/browser-read-2026-11-26/grid-caiso-reliability/reliability-table-1280.png` (the table at 1280 px, dots for the cells with no day); `docs/reviews/browser-read-2026-11-26/grid-caiso-reliability/reliability-390-page-scrolled-sideways.png` (390 px, the page pushed 150 px sideways: the text cut at the left edge).

## B1: the policy week grid (`/policy?view=week`)

Whose: no window's tonight. Read at 1280 and 390 px (`runs/c750/b_a11y.mjs`, `runs/c750/b_a11y2.mjs`).

- As it opens (the last 7 days): "0 actions" and no grid; the page says the actions are held ("license needed") and that the dockets were held on 12 November 2026. With "Last 30 days": 3 actions, a grid of two agencies by nine topics.
- **The fix is there.** Both buttons of the grid and both row totals have a name a screen reader says, the hover's own words ("Texas PUC: 2 actions on large-load tariff in the last 30 days"; "Texas PUC: 2 actions in all in the last 30 days"). The sixteen zeros are drawn at full strength in the muted color (5.6 to 1), each with its hover ("Texas PUC: 0 actions tagged large loads in the last 30 days").
- A press on the grid's first button (a finger at 390 px, the mouse at 1280): the address becomes `/policy?view=week&days=30&agency=txpuc&topic=large-load-tariff`, the button reads pressed, the count "2 actions", and the two Texas rows are listed (9 November and 30 October 2026, docket 60332, "no read yet"). No sideways scroll at either width (1265 of 1265; 390 of 390). One h1, then h2, then h3.
- Nothing to fix. One thing a reader will ask, already said on the page: the newest action is 9 November, seventeen days old, because nothing is extracted while the key is at its limit.

Pictures: `docs/reviews/browser-read-2026-11-26/policy-week/policy-week-as-it-opens-1280.png` (the last 7 days: no action); `docs/reviews/browser-read-2026-11-26/policy-week/policy-week-30-days-1280.png` (the last 30 days: the grid with its zeros at full strength).

## B2: the severance calculator's lists (`/severance`)

Whose: no window's tonight. Read at 1280 and 390 px with every credit of every state and product ticked in turn (`runs/c750/b_a11y2.mjs`).

- Every list and field of the calculator has a name, in every state (Texas, Louisiana, New Mexico) and product, with each credit chosen: no field without one.
- **The list the fix named is not drawn on production.** "Credit tier, <credit>" is drawn only for a tiered credit that carries no certified price. Both tiered credits in the rules file (Texas, low-producing oil lease and low-producing gas well) carry certified prices, so the page draws the "Report period" list in its place, and that list is named ("Report period, Low-producing oil lease credit, Exempt Type 11"). The fix stands in the code for the day a tiered credit without certified prices is added; there is nothing to see of it today. No fault.
- No sideways scroll with a credit ticked (1265 of 1265; 390 of 390).

Pictures: `docs/reviews/browser-read-2026-11-26/severance/severance-as-it-opens-1280.png`; `docs/reviews/browser-read-2026-11-26/severance/severance-credit-ticked-1280.png` (the last credit ticked).

## B3: one h1 a page and no level skipped (`/data/licenses`, `/map?tab=resources`, `/map?tab=queues`)

Read at 1280 and 390 px with every fold open (`runs/c750/b_a11y.mjs`). **The fix is there on all three:** `/data/licenses` has one h1 ("Licenses") and 22 headings in order, the record's own title now an h2; `/map?tab=resources` one h1 ("Where the resources are") and 59 headings in order, the method note's headings one level down; `/map?tab=queues` one h1 and "Every entry year" an h2. No sideways scroll.

- **D1, not a fault: the word "undefined" inside an address on `/data/licenses`.** Seen four times in the record of reads: "(answered at https://lustat.statec.lu/undefined)". The read of 20 November settled it (row E3 of `docs/reviews/browser-read-2026-11-20.md`): it is the publisher's own answer, its server sending a robots request to an address that ends "undefined", and the record (`warehouse/metadata/license_reads.csv`, reads 1560, 1565, 1582 and 1586) says what was answered. Not reopened; no request filed.

## B10: the two fixes that read landed and are not on main

Read on production on 26 November at 11:42 UTC (`runs/c750/b10.mjs`). Both faults are still there.

- **`/curtailment/where-when`, the trend by year switched to its table:** the column reads "CAISO, the whole system: curtailment, GWh" over solar alone (2025: 3,482; with wind and solar chosen the same heading stands over 3,766). The unlanded commit `4f3247287` names the fuel in the heading.
- **`/events/covid-2020` at 390 px:** 390 px wide as it opens; with a grid's chart switched to its table the page is 392 px wide (a table 739 px wide pushes its block past its column). The unlanded commit `923d4cb4f` keeps each block to its column.
- Row 2 of `docs/state/landing_request_portable_w2.md` asks for the two commits, ready, to be seen. The branch is the desktop's second window's and is not touched here.

Picture: `docs/reviews/browser-read-2026-11-26/events-covid-2020/covid-390-tables-showing.png` (390 px with the tables showing).
