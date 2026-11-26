# The browser read of 26 November 2026: everything landed since 20 November, and what lands tonight

Energy Research Warehouse (ERW). Chain 750 (`queue/done/750-night-26-november-portable-window2-browser-read.md`), the portable laptop's second window, sessions 11000 on. Every page is read on production (`https://erw-flame.vercel.app`) in the internal view, in the laptop's own Chrome driven by `site/scripts/browser.mjs`, at 1280 px with a mouse and at 390 px with a finger (touch events). No build is made here and no model is called. The scripts are in `runs/c750/` on the laptop (not in git); the pictures are in `docs/reviews/browser-read-2026-11-26/`.

How a row reads: what was done, what was seen, what should be seen, and whose it is. A site fault on a page no window owns tonight is fixed on a branch `wip/c750-<page>` with a test and is a row of `docs/state/landing_request_portable_w2.md`. A fault on a page another window owns tonight is a row here that names the window, and its code is not edited. A data fault is a row of `docs/state/data_requests_done_line.md`. A thing that is a choice is one line under "For Samuel's ruling" at the foot, with the page left as it is.

## Where things stand (kept current)

| | Count | Where |
|---|---:|---|
| Read | part A (5 rows); part B (all 14 of its list); part D (the five sellable tools, 28 more pages of the menu, the first minute); part C as it lands (the landing of 14:16 UTC and `/impact` with Datacenter so far) | each section below |
| Faults fixed here, each on a branch with a test | 8 (G1, C1, C2, GW1, K1, K2, K3, K4) on five branches | rows 1, 3, 4, 5 and 6 of `docs/state/landing_request_portable_w2.md`. G1, C1 and C2 landed at 14:16 UTC and are seen on production; the rest are seen in a build by the first window and requested |
| Faults filed for the window that owns the page | 9: L1 (two commits of the desktop's second window that read landed and were not on main: row 2, landed at 14:16 UTC and seen); CP1 and CP2 on `/cost-of-power` (the old laptop; window A); R1 on `/research` (the old laptop); I1 to I5 on `/impact` with Datacenter (window C) | part D and part C below |
| Known to their owner, read again when repaired | 1 (the page files of 21 to 25 November, L2) | chain 701, part C |
| For Samuel's ruling, the page left as it is | 10 lines | the foot of this file |
| Not on main yet at 15:10 UTC | `/forecast`, `/equities` and the board's new group, the All grids tab's new rows | part C, when they land |

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

- **The same sweep at 1280 px** (13:20 UTC, 145 addresses): clean; `/internal/waits` takes 7.9 s to load, as on 20 November.
- **The 173 addresses of the site's own check list** (`check-values --list`: the views with choices in their address, where a page's other states live), each at 390 px as it opens and then with every chart switched to its table and every fold open (`runs/c750/quiet_tables.mjs`, 13:30 to 13:45 UTC): no empty chart, no "undefined", no skipped heading, no error. Sideways scroll on four addresses, all three faults of this file: `/grid?grid=caiso` and `/grid/caiso` (G1, fixed), `/events/covid-2020` (row 2 of the landing file) and `/cost-of-power?view=grids` (CP1, filed). Nothing else is wider than its screen.

## B4 and row G1: the Grid tool's reliability table (`/grid?grid=caiso#reliability`)

Whose: no window's page tonight (the old laptop's Grid audit, chain 710 part D, is of the tool's figures). Read on production at 1280 and 390 px (`runs/c750/b_a11y2.mjs`, `runs/c750/b4_cause.mjs`).

- **The fix of 20 November is there.** The table "Every notice since 1998: days per year" has 226 cells with no day; each shows a dot in the muted text color (rgb 107, 103, 95 on white: 5.6 to 1) and is read aloud as "none". At 1280 px the page is 1265 of 1265 px wide.
- **G1, a fault the fix brought with it: at 390 px the page is 539 px wide.** Done: `/grid?grid=caiso` opened at 390 px. Seen: the page scrolls sideways to 539 px (the header, the text and every chart slide off to the left). Should be seen: 390 px, the table scrolling inside its own frame, as on 20 November. Cause, shown on production's own page: each "none" label is placed "absolute" (the class `sr-only`); the table's frame scrolls sideways but is not the labels' containing block, so it does not clip them, and the 60 labels of the columns past the frame's right edge (to 538 px) widen the whole page. With the labels hidden the page is 390 px wide; with the labels back and the frame made "relative", 390 px, the table still 526 px wide inside its 358 px frame and the cells still read "none". The session that added the labels had no browser, and the last phone sweep (20 November) was a day before they landed.
- **Fixed** on `wip/c750-grid-reliability` (`038ecbfcd`): the frame is `relative`; `tests/test_session11000_grid_reliability_phone.py` holds the rule for this component and fails on the code before. Row 1 of `docs/state/landing_request_portable_w2.md`, ready, to be seen. The other 145 addresses of the sweep keep to 390 px, so no other page has this today. The source was read for the same trap (`runs/c750/sr_only_scan.py`, 345 files): 37 other scrolling frames hold a label of this class and are not positioned, each one label, a table's caption or a heading at the frame's left edge, which cannot reach past the screen; the reliability table is the only one with labels in its cells. The same thing would happen in any of them the day a label is put in a cell of a wide table.
- **Seen in a build** by the laptop's first window (session 10401, about 12:00 UTC): 390 of 390 px, the table scrolling in its frame; row 1 marked requested.

Pictures: `docs/reviews/browser-read-2026-11-26/grid-caiso-reliability/reliability-table-1280.png` (the table at 1280 px, dots for the cells with no day); `docs/reviews/browser-read-2026-11-26/grid-caiso-reliability/reliability-390-page-scrolled-sideways.png` (390 px, the page pushed 150 px sideways: the text cut at the left edge).

## B6: grid conditions (`/conditions`), read in full

Whose: built by the data machine (chain 601); no window's tonight. Read on production on 26 November 11:48 to 11:55 UTC at 1280 and 390 px (`runs/c750/b6_conditions.mjs`). The page shows the files built 20 November (L2): its newest day is 20 November.

**Five cases, written first, then taken on the page.**

1. *A power trader:* on the last month's highest day, was ERCOT above its day-ahead forecast, and by how much? Opens the page as it stands. Answer on the page: the line at a glance names the day (65,888 MW on 2 November 2026); the daily table gives the forecast's peak beside it (65,196 MW), 692 MW under. Answered without leaving the page.
2. *A reliability analyst:* what do ERCOT's strips show over Winter Storm Uri? Chooses the event. Answer: demand served fell from 69,215 MW on 14 February to 46,846 MW on 16 February against a forecast peak of 75,061 MW; the adder was above zero in all 24 hours of 16 February; six notices, among them "ERCOT calls for rotating outages" on 15 February. The megawatts out of service, the figure this reader wants most, are blank ("source needed", with the reason on hover): by the rule, and said.
3. *A CAISO watcher:* in the September 2022 heat wave, how much was out of service, how congested was the grid, and which alerts were in force on each day? Answer: peak demand 51,104 MW on 6 September, 14,100 MW out in an hour on 9 September, 226 constraint-hours on 8 September, and that day's EEA 3 from 17:17 to 20:00. **The last day's alerts cannot be read: row C2.**
4. *A student:* SPP around one ordinary day, 24 July 2024. Types the day, presses Show. Answer: the fifteen days either side, day by day: that day's peak 49,395 MW against a forecast peak of 47,164 MW, 9,262 MW out in its highest hour, 224 constraint-hours. The page says why no hour is drawn (hours are kept for the newest days and the nine events).
5. *A reader on a phone:* ERCOT beside CAISO in the summer 2023 heat (row H4 of chain 601). Answer: the two operators stand one under the other, each with its own strips; the page is 390 px wide as it opens and with all twelve charts switched to their tables. H4 holds.

**Figures.** In seven views (the five above, CAISO beside SPP over the August 2020 heat, PJM beside MISO), every chart switched to its table: 21 lines at a glance and 15,553 table cells at each width set beside `site/data/conditions/<operator>.json`. All agree but the two alert lists of row C2. (One hour of PJM, 2 November 04:00 UTC, is a row of "not held" on the page and no row in the file: EIA's file lacks it; the page says the truth.) The hourly tables page 500 rows at a time and say so ("Rows 1 to 500 of 865", Earlier, Later).

**The hand, at both widths (11 of 11 checks).** Each chart gives a card inside the screen under the mouse and under a finger ("2026-10-24 17:00 UTC Demand 55,830 MW Day-ahead forecast 56,214 MW"); a choice goes into the address and the page draws it; after the back button the Operator list reads what the page draws; a link carrying two operators and an event opens on them; a day typed and Show keeps the operator; a day before the file (1 January 2010) and a wrong operator in the address break nothing (no empty chart; the second opens ERCOT); the decisions fold opens and its eight marks each open a box with a default and a source inside the screen (84 to 372 px at 390 px); the keyboard alone reaches the foot in 28 stops, each seen and marked.

**Quiet faults.** None: no sideways scroll in any view at 390 px, no empty chart, no "undefined", "NaN" or "null", a blank strip a dashed box with its reason. Usable in 1.4 s as it opens (0.3 to 0.5 s for a second view).

| # | Done | Seen | Should be seen | Whose, and state |
|---|---|---|---|---|
| C1 | Any view; the small line under each operator's name | "days and hours in America/Chicago clock time for days and hours" (the page wraps the file's `time`, which is already the whole phrase) | The clock said once | no window's; **fixed** on `wip/c750-conditions` (`569d15885`), with a test |
| C2 | CAISO, the September 2022 heat wave; and CAISO over the August 2020 heat | The heading reads "Alerts and notices in force, 2022-08-31 to 2022-09-09 (44)"; the table under it has 40 rows and stops at 8 September. Nothing says the list is cut. Missing: 9 September's EEA 1 (16:00 to 20:00), EEA Watch, Flex Alert and RMO. Over August 2020: "(79)" and 40 rows, nothing after 17 August | Every notice the heading counts, or a line saying which are left out | no window's; **fixed** on `wip/c750-conditions` (every notice is a row), with a test that fails on the code before. Landing row 3, ready, to be seen |
| C3 | Any blank strip, at 390 px with a finger | "Out of service: source needed" in a dashed box. The reason (ERCOT publishes this only on paths its robots file disallows) is the browser's own tooltip: a tap opens nothing. The table "What is held for each grid" says "on hover" too | On a phone, some way to read why a strip is blank | site-wide (part A, point 1); one line under "For Samuel's ruling"; the page left as it is |

Pictures: `docs/reviews/browser-read-2026-11-26/conditions/conditions-as-it-opens-1280.png` (ERCOT, the newest 35 days); `docs/reviews/browser-read-2026-11-26/conditions/conditions-caiso-september-2022-1280.png` (its most telling choice: CAISO over the September 2022 heat wave, three lines at a glance); `docs/reviews/browser-read-2026-11-26/conditions/conditions-two-operators-390.png` (ERCOT beside CAISO at 390 px).

## B11: where the grid is congested (`/congestion`), read in full

Whose: built by the data machine (chain 601); no window's tonight. Read on production on 26 November 11:55 to 12:00 UTC at 1280 and 390 px (`runs/c750/b11_congestion.mjs`). The file is the one built 20 November (L2).

**Five cases, written first, then taken on the page.**

1. *A developer siting a load in SPP:* which constraints bound most in 2026, and what did each cost? Opens the page. Answer: of 1,880 constraints over 324 days, the one that bound most hours is SOONER_SONR_SONR_PHSHFT_PS (6,942 hours, mean shadow price 4.77 USD/MWh), and the one whose shadow price summed highest is TMP128_29363, contingency 333 (2,637 hours, mean 125.19, summed 330,132). The two lists stand one under the other, each under its own heading. Answered.
2. *A trader:* when does the constraint that cost second most bind? Presses its name in the list. Answer: OSAWEBCLESOO, contingency 33380: the hour-by-month table is darkest in October and November just after midnight (75 hours in October's hour 1), and the chart by month runs to October 2026. Answered at 1280 px under the mouse; at 390 px the table's cells are colors only (row N2).
3. *A CAISO analyst:* California's constraints of 2025. Chooses CAISO and 2025. Answer: 721 constraints, 69,868 constraint-hours; most hours 24723_CONTROL (4,567); highest sum 39021_SC21ATP (553,893). Answered.
4. *An investor:* SPP's two hubs side by side in 2025. Answer: the North hub's mean congestion part was -3.69 USD/MWh (13.1 percent off its price, 6,069 hours taking off), the South hub's -2.90 (9.9 percent); the monthly lines and the two hour-by-month tables stand together. Answered.
5. *A student:* which SPP constraint has bound most since 2014? Chooses "Every year held". Answer: TEXAS_CO_TXPS_TXCO_PHSHFT_PS, 60,293 hours; by sum, OSAWEBCLESOO, 1,999,437. Answered.

**Figures.** In seven views at each width: 1,715 marked figures (each against its key in `site/data/conditions/congestion.json` and against the words on the screen), 350 ranked rows (the file's own top lists in the file's order; 1,400 cells), 4,608 cells of the hour-by-month tables read through their hover words, and 1,218 monthly figures with every chart switched to its table. 166 of 166 checks agree at 1280 px and at 390 px.

**The hand, at both widths (12 of 12).** Each chart gives a card inside the screen; a press on a constraint's name opens when it binds and the Constraint list reads the same; after the back button the list reads what the page draws; choosing CAISO and Show draws a CAISO constraint (the constraint list still holds SPP's names until Show is pressed, and the page then takes CAISO's first); a link carrying two places and their year opens on them; wrong values in the address break nothing; the decisions fold's eight marks open inside the screen; the keyboard reaches the foot in 90 stops, each seen and marked.

**Quiet faults.** None: no sideways scroll (the hour-by-month tables, 760 px wide, scroll inside their 358 px frames at 390 px), no empty chart, no "undefined", no skipped heading. Usable in 1.2 s as it opens.

| # | Done | Seen | Should be seen | Whose, and state |
|---|---|---|---|---|
| N1 | The two ranked lists | "Highest: 1080.08 USD/MWh" with no thousands comma, beside "Summed: 330,132" with one | One form in a table | a choice the gate's check pins (`check-values`: "USD/MWh to two decimals without a thousands comma"); for Samuel's ruling, the page left as it is |
| N2 | An hour-by-month table at 390 px, a finger on a cell | Nothing: each of the 288 cells is a color whose figure is its hover (which is also what a screen reader is given). The line under the table gives only the darkest cell's figure | On a phone, some way to read a cell | site-wide (part A, point 1); for Samuel's ruling |
| N3 | CAISO's lists | "HUMBOLDT_IMP_NG (contingency Base Case)": the base case is written as a contingency, where SPP's base case has no suffix | The same form for both, or CAISO's word kept as the operator's | a choice of words; for Samuel's ruling |

Pictures: `docs/reviews/browser-read-2026-11-26/congestion/congestion-as-it-opens-1280.png` (SPP, 2026, the list of constraints that bound most); `docs/reviews/browser-read-2026-11-26/congestion/congestion-two-hubs-1280.png` (its most telling choice: SPP's two hubs side by side, the table of places above and the months below).

## B7: the thirteen regions in the Grid tool (`/grid?region=<region>`), on the files rebuilt 21 November

Whose: no window's page tonight (the old laptop's audit, chain 710 part D, is of the tool's figures and edits no page). Read on production on 26 November 12:01 to 12:06 UTC (`runs/c750/b7_regions.mjs`).

- **Figures, 1280 px:** for each of the thirteen regions' Mix tab, with every chart switched to its table: the latest hour held, the 840 hours of the last 35 days, the average day of the latest month and the month's shares, each cell against `site/data/regions/mix/<region>.json`: 94,435 cells, 221 of 221 checks agree. The Clean and Network tabs of each region open with their heading and no quiet fault.
- **390 px:** the latest hour of each region against its file (104 cells), no sideways scroll as each opens and with every table shown, no empty chart, one h1: 117 of 117.
- **What a reader sees first is six days old (L2).** "The latest hour held" reads 20 November 2026 for ten regions (04:00 to 07:00 UTC), 19 November 06:00 for the Southwest and 18 November 04:00 for the Carolinas. The page is true to its file; the file is the one built 21 November 01:10 UTC. Window A's repair tonight (chain 701, part C, item 3) brings the newer files; this row is read again then.
- Each page loads in 0.3 to 1.8 s. No fault of the pages.

Picture: `docs/reviews/browser-read-2026-11-26/grid-regions/grid-tennessee-as-it-opens-1280.png` (Tennessee's Mix tab: the latest hour held, 20 November 05:00 UTC).

## B9: chain 620's ten fixes and the tour's eighth stop, on production

Whose: the portable laptop's own fixes of 20 November, seen in a build by the desktop's second window, landed 21 November 00:10 UTC; no browser had read them on production. Read 26 November 12:04 to 12:08 UTC with the site's own checks and chain 620's script (`site/scripts/check-back-button.mjs`, `site/scripts/check-tour.mjs`, `runs/c750/b9_fixes.mjs`). **All are there.**

| Fix | Seen on production |
|---|---|
| The back button on lists that submit themselves | `check-back-button`: 16 of 16 on `/queues/places`, `/storage/places`, `/curtailment/where-when`, `/ai-energy` (after the back button each list reads what the page shows; on 20 November 0 of 6 pages did) |
| `/internal/findings` on a phone | 390 of 390 px (470 before) |
| The resource set's legend | the worked example reads lowest 1.58, highest 6.91 kWh/m2/day, each figure's hover naming the part of the layer it is read from (Alaska, Hawaii); the map's legend for the same layer runs 1.6 to 6.9 |
| The Grid panel's words for an exporter | Seminole Electric: "It sent out, net, power equal to 592 percent of its demand."; TVA, an importer, reads as before |
| The tour's headings and its eighth stop | `check-tour`: 101 of 103; the two that fail are the Digest stop's headings ("Top of the industry", "ERW's Numbers Today"), left for Samuel's ruling on 20 November and still his |
| The price map's window | the hover names its days: "34.86 USD/MWh at HB_HUBAVG, day-ahead, the 365 days to 2026-11-16"; "the 30 days to ..."; the day itself for a day's price. The day is 16 November: the price map's file is the one of 19 November (L2) |
| `/policy` when its list is held | the heading, the three views, and "The list of every action is not drawn here: license needed" |
| A transmission line's end HIFLD does not name | "an end HIFLD does not name (its mark UNKNOWN202457) to FRANNIE"; a line with both ends named reads as before; no hover prints the mark as a place |
| Six method pages on a phone | each 390 px wide (the whole set of method pages is swept in B13) |
| `/data/faults` on a phone | 390 px wide (417 before) |

Pictures, one a fix that draws something: `docs/reviews/browser-read-2026-11-26/chain-620-fixes-on-production/` (`authority-sent-out-1280.png`, `price-window-1280.png`, `line-end-unnamed-1280.png`, `resource-set-legend-1280.png`, `policy-1280.png`, `findings-390.png`).

## B8: the problem edition of 21 November (`/learn/problems`)

Whose: the data machine's edition file; the pages are no window's tonight. Read 26 November 12:09 UTC at 1280 and 390 px (`runs/c750/b8_edition.mjs`). `/problems` is no address; the sets are at `/learn/problems`.

- The index lists the edition's ten sets; each set's page links the edition of 2026-11-21; each dated edition and its teacher page open and name their date (30 pages a width).
- **Words and figures:** the 59 questions' words are on the edition pages, and each figure of the answers, their lines and their steps is on the teacher pages as the file `site/data/problem_editions/2026-11-21.json` gives it: 838 checked, none missing.
- **The irradiance question** (the reason the edition was made): the teacher page answers "Global Horizontal Irradiance 6.91 kWh/m2/day; Direct Normal Irradiance 9 kWh/m2/day: 1.30 times", the legend the map draws. The edition of 20 November keeps its 6.50, as an edition does.
- No sideways scroll, no empty chart, no skipped heading, no "undefined" at either width: 82 of 82 checks at each. No fault.

Pictures: `docs/reviews/browser-read-2026-11-26/problem-edition/problems-index-1280.png` (the ten sets); `docs/reviews/browser-read-2026-11-26/problem-edition/resource-set-edition-1280.png` (the resource set's edition of 21 November).

## B12 and B14: the events, demand and supply pages on the real region files, and the five pages of the reader-page tests

Read 26 November 12:25 to 12:29 UTC at 1280 and 390 px, each as it opens and then with every chart switched to its table and every fold open (`runs/c750/quiet_tables.mjs`): the nine events' whole-country sections (a different pair of regions each), four pairs on `/demand?view=country`, four on `/supply#whole-country`, and `/ai-energy`, `/industry`, `/queues/places`, `/storage/places`, `/curtailment/where-when`. 22 addresses a width.

- **No quiet fault but the one already filed:** no sideways scroll but `/events/covid-2020` at 390 px with its tables showing (392 px, row 2 of the landing file); no empty chart; no "undefined", "NaN" or "null"; no skipped heading; every page loads in 0.3 to 2.2 s.
- The figures of these pages were set beside their files in full on 20 November (the desktop's second window: 6,431, 11,119 and 912, none differing) and part A read the five rows that changed after; they are not counted again.
- **Two tables read again on the files rebuilt 21 November** (15:02 to 15:06 UTC, both widths). `/supply`, the mix by month, for eight pairs of regions and years (`runs/c750/b12_supply_mix.mjs`): 1,670 cells (each source's share, the net generation in GWh, the days held) agree with `site/data/regions/mix/<region>.json`; each of the nine months the files leave out is a row of "not held yet"; a year a file leaves out whole (the Northwest's 2020) is one line "not held yet" under its chart. `/demand?view=country`, the table of days, for seven pairs of places (`runs/c750/b12_demand_days.mjs`): 196 cells (the day's GWh and its highest hour) agree with the demand files, a day not held whole reading "not held", and the table reaches each file's newest day.
- **One thing seen on all of them, not new and site-wide:** a chart switched to its table prints "not held" where a series has no value, and that blank gives no reason on hover. On these 22 pages 1,206 of 3,218 blanks are of this kind (the other 2,012, the tables the pages draw themselves, each give their reason). The shared chart table knows only that the value is missing, not why. One line under "For Samuel's ruling".

## B13: the variables table on the method pages (`/data/methods/<note>`)

Whose: the desktop's second window's tonight (chain 730): read, never edited.

- The file the table is drawn from (`site/data/codebook_methods.json`) and its component last changed on 20 November 14:07 UTC, before chain 620 read 473 method pages cell for cell (10,443 variables, none differing), and no branch of tonight touches either. The cells are not read again.
- On the first twelve pages at 390 px (`runs/c750/methods_sweep.mjs`): each draws its variables (186 in all), nine of them as one block a variable, as the component means at a phone's width; none scrolls sideways; no row with an empty name or label.
- **The sweep of all 616 method pages at 390 px did not finish:** it was stopped by Claude Code at about 12:23 UTC, the laptop critically low on memory while the session waited on it (the first window was building). It is not started again unless asked. What stands in its place: the six pages chain 620's fix mended are 390 px wide (B9), and the full sweep of 20 November found no other.

## B5: the findings review page's charts (`/internal/findings`)

The branch behind this row (`wip/9820-findings-charts`, the desktop's fourth window) changed how the warehouse draws a finding's picture (`warehouse/analysis/findings/card_image.py`, `deep/redraw.py`) and no page code, so nothing on the page changed with its landing; a draft's picture changes only when it is drawn again. The page as it stands on production: 42 charts, none empty, 1265 of 1265 and 390 of 390 px wide, no error in the console; it takes 4.7 s to load at 1280 px and 3.5 s at 390 px (the slowest page of the list, under five seconds). No fault.

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

## Part D: the sellable tools, at 1280 and 390 px

Read on production on 26 November from 12:30 UTC, while none of tonight's pages had landed. Figures by the site's own `check-values` (each marked figure fetched in the internal view and set beside Supabase's public REST view; run in the foreground on each tool's own addresses); the hand by `runs/c750/d_battery.mjs` and `runs/c750/d_tool.mjs`.

### What a battery earns (`/cost-of-power/battery`)

Whose: no window's tonight (its model was audited on 20 November; that audit's branches are the old laptop's).

**Five cases.** (1) *A developer:* what did a 100 MW, 4-hour battery in ERCOT earn over the last twelve months? The page's first sentence: USD 80.40 per kW (USD 8.04 million), 33 percent of it from ancillary services. (2) *A lender:* did it cover its debt, and what does a bad month look like? 2.58 times; the 10th-percentile month of the last 36 is USD 475,477 (December 2024). (3) *A CAISO developer:* 4 hours on the day-ahead schedule: choosing CAISO and then the schedule puts both in the address and the sentence reads USD 65.96 per kW, debt covered 1.94 times. (4) *An investor:* is it worth building, and how much does the capital cost matter? With the capital cost changed from 1,110 to 800 USD per kW the coverage goes from 2.58 to 3.58 and the address carries `ac=800`; the field's Reset puts every figure back. (5) *A reader on a phone:* a link carrying 2 hours opens on 2 hours (USD 57.90 per kW, 47 percent from ancillary services), every figure's key saying so. Each answered on the page.

**Figures.** `check-values` on the tool's 13 addresses (both grids at 2, 4 and 8 hours under both strategies, the scenario and assumption addresses, the awards page) with the generator page's four: 988 of 988 match Supabase.

**The hand, 24 of 24 at each width.** Every control has a name; the units switch, the grid and the strategy each carry into the address; after the back button the choices read what the address says; a held grid in the address (PJM) leaves the page on ERCOT with PJM's choice disabled and "license needed" beside it, and no figure of PJM is drawn; the fifteen boxes of the headline and chart pickers each change the page and change it back; the nine "About" marks each open a box inside the screen; both charts give a card under the mouse and a finger; the keyboard reaches the foot (85 stops at 1280 px, 35 at 390 px, where the assumptions are folded), every stop seen and marked. No sideways scroll after any step, with every fold open, at 390 px. Usable in 0.4 s. **No fault.**

**The Price years list and the back button** (15:12 UTC, both widths, `runs/c750/battery_back.mjs`). The list writes its choice over the page's own place in the browser's history (`/cost-of-power/battery` becomes `/cost-of-power/battery?py=year_2024`, the history as long as before), as the code says it means to ("written in place so that a comparison can be shared as a link"): one step back leaves the tool for the page before it. On the generator's page the same list adds a step, and the back button puts the earlier years back within 2 s. Each works as written; the two pages differ. Line 11 under "For Samuel's ruling".

Pictures: `docs/reviews/browser-read-2026-11-26/battery/battery-as-it-opens-1280.png`; `docs/reviews/browser-read-2026-11-26/battery/battery-caiso-day-ahead-1280.png` (its most telling choice: CAISO on the day-ahead schedule).

### What a generator earns (`/cost-of-power/seller`)

Five views as five cases: a solar developer in ERCOT (opens: USD 59.85 per kW over October 2025 to September 2026, against a long-run USD 102.24 a year; the price it received was USD 23.27 per MWh), a battery selling energy alone (USD 58.53), a gas peaker (a margin over fuel of USD 48.15), a wind plant in SPP at the North hub (USD 83.59; "SPP holds one full year, 2025 ... There is no long-run average yet"), a solar plant in CAISO at SP15 (USD 28.45; 51.6 percent below the flat average price). Each first sentence answers its reader.

- **Figures:** in the 988 of 988 above.
- **The hand, 70 of 70 at 1280 px and 69 of 69 at 390 px:** no quiet fault as each opens or with every table shown and every fold open; every control named; both charts give a card; no mark's box past the screen; the keyboard to the foot (79 to 94 stops). Each view loads in 0.3 to 1.5 s. **No fault.**
- Noted on 20 November and unchanged: this tool's last twelve months end in September 2026 and the battery tool's in October.

Picture: `docs/reviews/browser-read-2026-11-26/generator/generator-as-it-opens-1280.png`.

### Automated Analysis (`/research`, its cards, `/attention`)

- **Five cases, each taken on the page** (`runs/c750/d_cases.mjs`; nothing was submitted, since a request would call a model). (1) *A reporter:* did batteries eat their own lunch? The card answers in its first paragraph: Texas' fleet went from 87 MW to 19,195 MW and its worst-interval multiple from 126.6 times in 2019 to 12.1 in 2025; New York, with 269 MW, went the other way; "California spoils the story". (2) *An analyst:* how often is power below a gas plant's fuel cost? "ERCOT's hub average sat below a gas plant's fuel cost in 38.8 percent of 2019's hours and 40.9 percent of 2025's", with what the share does not say. (3) *A siting lead:* where a gigawatt pays least: "least all-in at ERCOT HB_WEST: USD 41.83 per MWh ... most at ERCOT LZ_AEN: USD 47.63", and that only 14 of the tab's 48 rows hold every part. (4) *A reader who wants a cut of their own:* the request form is there with its words on what is kept ("Stored with the request and used to send the answer"); not sent. (5) *A reader of the news:* `/attention` says what it rests on: 8,119 of 27,419 stories classified, five weeks, built 16 November, by a model's reading. Each answered on the page.
- **Figures:** `check-values` on `/research`, five cards, `/attention` and the Grid tool's addresses together: 1,377 of 1,377 match Supabase.
- **The hand, 65 of 65 at each width** on `/research`, three cards and `/attention`: no quiet fault, every control named (242 buttons on `/research`), each card's charts answer the mouse and a finger with their figures ("2021-01 ERCOT: Worst-interval multiple (P99.9 / median): 19.37"), the keyboard reaches the foot (377 stops on `/research`). Each loads in under a second.
- **Row R1, words that are not true, for the old laptop (window D, chain 710, whose audit of Automated Analysis runs tonight): the small example charts.** Done: the mouse passed over each of the six small example charts of `/research` at 60 places, and a finger at 390 px (`runs/c750/d_research_hover.mjs`, `d_research_titles.mjs`). Seen: no card and no value; each example holds one tooltip, its own name ("Example: Small multiples: ERCOT"). The line above them says "drawn small: real values, hover reads them" (and, for a template, "Hover reads the values."). Should be seen: either the values under the hand, or a line that does not promise them. The cause is plain in the code: the picker's small example is drawn with no card by design (`site/components/svgchart.tsx`, `small`: "no toggle, no card, no names"), and the sentence in `site/components/analysis/RequestFlow.tsx` was written as if it had one. The large charts of the same page do answer (18 of 18 places). Not edited here. Also line 8 under "For Samuel's ruling".

Picture: `docs/reviews/browser-read-2026-11-26/automated-analysis/research-as-it-opens-1280.png`.

### The Grid tool (`/grid`)

Whose: no window's page tonight. The old laptop's audit of its figures (chain 710, part D) is written and on main (`docs/reviews/grid-model-audit-2026-11-26.md`, six findings on `wip/audit-grid-1` to `6`); none of them is the row below.

- **Five cases, each taken on the page** (`runs/c750/d_cases.mjs`, 14:57 UTC). (1) *A trader:* ERCOT's demand in the latest hour against a week ago: "In the hour starting Nov 24, 5:00 PM CST, the latest EIA has published, ERCOT used 58,034 MW, more than the 52,167 MW of the same hour a week earlier." (2) *A carbon accountant:* how clean CAISO's power is: the Clean tab's charts and tiles, each a checked figure. (3) *A developer:* what PJM sends and takes: "In the hour starting 2026-11-23 06:00 UTC, PJM sent ...", with the page's own words that the hour is two days old because EIA publishes interchange late. (4) *A student:* the Lower 48's mix: "Natural gas was its largest source: 245,481 MW of the 509,295 MW generated". (5) *A storyteller:* Texas during Uri on the network: the story is offered and plays ("Showing: Texas during Uri, 2021-02-07 to 2021-02-24. 0 pair-hours not reported by either side"). Each answered without leaving the page; the ten addresses of these cases and Automated Analysis' keep to 390 px.
- **Figures:** `check-values` on every address of the tool in its list (the eight grids in each view, the Network and Gravity shapes, the alerts page): in the 1,377 of 1,377 above. The thirteen regions: B7.
- **The hand** (`runs/c750/d_tool.mjs`) on the Lower 48's Mix tab, ERCOT's Mix, Clean and Exchange tabs, PJM's Mix tab and the Network view: 81 of 81 at 1280 px, 80 of 81 at 390 px; the one miss was this read arriving while the page was still going back, and the back button was then tried 18 times on the tool's two lists at both widths, each time reading what the page shows (`runs/c750/d_grid_probe.mjs`). Every control named; each chart gives a card under the mouse and a finger but the Exchange tab's circles (whose figures are in the list beside them); the keyboard reaches the foot (65 to 138 stops). Loads in 0.5 to 2.7 s.
- **Samuel's standing rulings, each looked for on the Network view at both widths, all there:** light mode only (a white page, no switch to dark); the free-floating 3D network; carbon intensity the color that opens ("Carbon intensity of generation: 158 to 355 kg CO2/MWh; grey: not held"); no name drawn on the network; the "Watch" stories (Live now, California's evening, Texas during Uri, The June 2025 heat); the side panel; the Batteries switch (off as it opens).
- **Row GW1, a fault: "Same day last week" loses its first hours.** Done: on each of the seven grids' pages, the chart "hourly demand today so far and the same day last week" switched to its table (`runs/c750/d_grid_lastweek.mjs`, 13:02 UTC). Seen: last week's column reads "not held" for the day's first 5 hours on CAISO, 7 on ERCOT and SPP, 8 on PJM, MISO, NYISO and ISO-NE; it starts at 13:00 UTC on every grid. Should be seen: all 24 hours; the live set holds them (24 of 24 hours of 17 November for ERCOT, PJM, CAISO and the Lower 48, read through the public REST view, `runs/c750/live_days.py`). Cause: the page reads nine days of demand back from the clock (`site/lib/grid.ts`), while its "today" is the latest day EIA has published, 24 November, two days behind the clock; last week's day began before the read does. The cut grows by an hour every hour until the next load, and the line is whole only while the loads are less than a day behind. **Fixed** on `wip/c750-grid-last-week` (`aad80aaba`): the read reaches sixteen days (the lag plus eight are needed), for the page and for the Now view's "same hour a week earlier"; `tests/test_session11000_grid_last_week.py` works the rule through and fails on nine days. Landing row 4, ready, to be seen.
- **Row GW2, noted: the address while a story plays.** The Network view says "The address holds what you are looking at: copy it to share the view." A typed day goes into the address at once, and so does a grid chosen from the list; each opens the same view fresh. A Watch story starts playing when it is pressed, and while it plays the address stays as it was: copied then, it opens the live week (3 of 3 stories, `runs/c750/d_grid_story.mjs`). Once the story is paused the address takes the story, its hour and the grid, and opens the same view and hour fresh (`d_grid_story2.mjs`). The code says why (the address would change five times a second while it plays). Not a fault of function; line 10 under "For Samuel's ruling".
- G1 (the reliability table at 390 px) is above, in B4.

Pictures: `docs/reviews/browser-read-2026-11-26/grid-tool/grid-as-it-opens-1280.png` (the Lower 48, Mix); `docs/reviews/browser-read-2026-11-26/grid-tool/grid-network-1280.png` (the Network view's controls: the Watch stories, the day, the two switches).

### What a datacenter pays (`/cost-of-power`): read, never edited

Whose: the old laptop audits it tonight (window D, chain 710, part B: `docs/reviews/datacenter-model-audit-2026-11-26.md`, branches `wip/audit-datacenter-*`), and window A (chain 701) is writing the All grids tab's files and its large-load rows. Its faults are rows here for those windows; no code of it is touched.

- **Figures:** `check-values` on every address of the tool in its list (35, the views of the All grids tab among them): 2,777 of 2,777 match Supabase.
- **The hand** (`runs/c750/d_tool.mjs`, five views): no quiet fault as each opens; every control named; each chart gives a card; no mark's box past the screen. The page as it opens answers its reader in one sentence ("A flat 100 MW load at LZ_NORTH in ERCOT, buying real time, paid USD 34.07 per MWh over the last twelve months, USD 29.85 million in all: USD 0.0691 per GPU-hour for power alone"). It takes 3.3 to 3.8 s to load as it opens and 2.8 to 4.3 s on the All grids tab: under five seconds, the slowest tool of the five.

| # | Done | Seen | Should be seen | Whose |
|---|---|---|---|---|
| CP1 | `/cost-of-power?view=grids` at 390 px; a finger on the Table switch of "When is power cheap: real-time price by hour of day" (`runs/c750/d_cop_probe.mjs`) | The page becomes 1,677 px wide: the table has 25 columns (1,661 px), and the frame that should scroll it is itself 1,661 px wide, so the whole page scrolls sideways. Pressing Chart again does not bring it back; the page stays 1,677 px wide until it is opened again. The other two tables of the view keep to their 358 px frames | 390 px, the table scrolling inside its frame | window D (the old laptop's audit of this page). The frame grows with the table because the block around the chart is not held to its column (the same cause as `/events/covid-2020`, whose fix is `min-w-0` on the block) |
| CP2 | `/cost-of-power?view=allgrids` (and with `rows=nodes`); the Profile list changed to "flexible" (the address takes `profile=flexible`, the page says "A flexible compute load of 100 MW ..."); then the browser's back button. Two tries a view at each width, read for five seconds after going back | The address goes back to `/cost-of-power?view=allgrids`. The page does not: the list still reads "flexible" and the sentence still says "A flexible compute load", under the datacenter's address. 8 of 8 tries | After the back button the page shows what its address says (the datacenter load), as the lists of chain 620's fix now do | window A (the All grids tab is its tonight) and window D. After the back button a copied address opens another view than the one on the screen. Watched again for 24 s at 15:08 UTC (`runs/c750/push_back.mjs`): the page never goes back, so it is not a slow load. The other forms that push a choice into the address the same way do follow the back button, within 2 s: the tool's own form (ERCOT to CAISO and back) and the generator's (solar to peaker and back) |
| CP3 | The All grids tab, the keyboard alone from the top | 500 stops and the foot not reached: 436 of them are the "About" marks of the table's rows (467 on the nodes view) | Noted, not a fault of function: every stop is seen and marked | for Samuel's ruling (line 9) |

Pictures: `docs/reviews/browser-read-2026-11-26/datacenter-pays/cost-of-power-as-it-opens-1280.png`; `docs/reviews/browser-read-2026-11-26/datacenter-pays/cost-of-power-grids-390-after-one-table.png` (CP1: 390 px after one tap on Table, the page pushed sideways).

### The rest of the menu, by hand

The pages of the menu that no window owns tonight, each walked at 1280 and 390 px with the same checks as the tools above (`runs/c750/d_tool.mjs`): `/prices`, `/prices/compare`, `/supply`, `/contracts`, `/severance`, `/battery/customer`, `/shoulder` (92 of 92 checks at each width); `/demand`, `/curtailment`, `/datacenters`, `/storage`, `/deals`, `/companies`, `/events` (89 of 92: the three are the rows below). Every page opens in under 1.6 s with no quiet fault. The charts of `/prices/compare`, `/shoulder` and `/demand` give their figures only as the browser's own tooltip, as the read of 20 November noted (its row S2); not reopened. Then fourteen more (14:42 to 14:52 UTC): `/map`, `/deals/capital`, `/policy`, `/thesis`, `/play/battery`, `/learn/bill`, `/states` (92 of 92 at each width); `/industry`, `/ai-energy`, `/queues/places`, `/storage/places`, `/explore/ercot-peak-premium`, `/explore/demand-growth`, `/explore/interconnection` (98 of 98 at 390 px; 96 of 98 at 1280 px, the two a read that came while the page was still going back: tried again with longer waits, 6 of 6). No fault on these fourteen.

| # | Done | Seen | Should be seen | Whose, and state |
|---|---|---|---|---|
| K1 | `/companies`, each field asked for the name a screen reader is given (`runs/c750/fields_named.mjs`, every page with a fixed address: 82 pages, 392 fields) | Five of the page's six fields have none: the Name box and the Kind, Segment, Grid and Has lists. Each stands in a label with an "i" mark before it, and a label names the first field inside it, which is the mark's own button ("About The search"). A screen reader says "search, edit text" and nothing more. No other page of the 82 has a field with no name | Each field named | no window's; **fixed** on `wip/c750-companies` (`d6dc93397`): each field carries its name; with a test |
| K2 | `/companies`: Kind set to OEM, Show (2 of 12,724 companies), then the browser's back button; the same with State (`runs/c750/d_companies_probe.mjs`, 4 tries at each width) | The address and the table go back to all 12,724 companies; the list still reads "OEM" (or "CA"). 4 of 4 | The list reads what the page shows | no window's; **fixed** on the same branch: the form keeps no state (`autocomplete="off"`), which was tried on production's own page first: 4 of 4 then read the page's value. Chain 620's fix of 20 November mended the lists that submit themselves; this form submits with its button and was not among them. Landing row 5, ready, to be seen |

**K2 is a class, so every form of its kind was tried.** The source was read for forms that submit with their button and hold a field that takes its value from the page once (`runs/c750/forms_scan.py`: 20 GET forms, 14 of them all mended lists or with no such field), and each of the others was tried in the browser at both widths: one field changed, the form's own button pressed, then the back button (`runs/c750/forms_back.mjs`).

| # | Done | Seen | Should be seen | Whose, and state |
|---|---|---|---|---|
| K3 | `/prices/compare`: A set to SP15, the form's button, then the back button; the same with B | The page goes back to no A; the list still reads "caiso:TH_SP15_GEN-APND". 4 of 4 | The lists read what the page shows | no window's; **fixed** on `wip/c750-forms-back` (`9eb8fbcbc`) |
| K4 | `/conditions`: a day typed (2024-07-24), Show, then the back button | The page draws the newest 35 days again; the Day box still reads the day. 4 of 4. (Its three lists were already right: they are the mended kind) | The Day box empty, as the page shows | no window's; **fixed** on the same branch. The mend, the form keeping no state, was tried on production's own pages first: 8 of 8 then read the page's value. Landing row 6, ready, to be seen |

**A link that carries a choice, opened fresh, on the pages that write the address themselves** (15:10 UTC, both widths, `runs/c750/fresh_links.mjs`). A layer switched on in `/map?tab=resources` (the address takes `on=wind_speed_100m,wind_capacity_factor` with the zoom and centre), a grid picked in `/research`'s library (`?grid=ercot`) and a row opened in the board's workbench (`/board?s=ercot-hb-hubavg-da`: "ERCOT Hub average day-ahead, 46.31 USD/MWh on 25 Nov 2026"): each address opened fresh shows what the hand had chosen, 6 of 6. The policy monitor's state list was not found by the script and is not counted.

`/industry` and `/states` read right after the back button. Two forms of the same shape could not be tried and are not changed: `/deals` (its list is held for a license, so no form is drawn) and `/severance/lease/real` (drawn only once a file is given).

### The first minute, as production stands before tonight's landings

Read 26 November 13:18 UTC with chain 620's own script (`runs/c750/d_first_minute.mjs`), as a stranger and as a reviewer, at 1280 and 390 px.

- **A stranger** meets the in-review page at every address, by the owner's instruction of 8 October; `/internal/findings` answers "No page at this address" to one. Nothing of the site is shown.
- **A reviewer:** the home page opens in 0.3 s; the menu's six groups hold 33 entries; the 54 distinct addresses of the menu, the home page, the foot and the tour were each asked for: 54 of 54 answer with their heading (`/ask` answers through its redirect to the Grid tool, as designed). Each group of the menu opens inside the screen at both widths. The keyboard's first stops are "Skip to content", the home link, the six groups, then the Digest, the Roundup and Email.
- **Unchanged since 20 November, and already rows there (not reopened):** the in-review page's heading for the home address is "/" (row D8 of the read of 20 November, for Samuel's ruling); at 390 px an open group of the menu covers the groups under it, so the next needs a second press (row D9, noted).
- **Tonight's pages are not in the menu, on `/in-review` or in the tour yet** (none has landed); this is read again when they are.

Pictures: `docs/reviews/browser-read-2026-11-26/first-minute/` (`a-stranger-at-the-home-page-1280.png`, `the-home-page-internal-view-1280.png`, `the-menu-open-390.png`).

## Part C: what landed tonight, as it landed

### The landing of 14:16 UTC (`task/c701-desk-3`), read on production at 14:23 UTC

Production showed the earlier build at 14:18 and 14:20 UTC and the new one from about 14:21:50 (`runs/c750/c_landed.mjs`, three reads). It brought `/impact` with Datacenter (window C), this window's rows 1, 2 and 3, and the old laptop's audit fixes of words.

**This window's three rows, seen where a reader meets them, at 1280 and 390 px:**

| Row | Before (14:18 UTC) | After (14:23 UTC) |
|---|---|---|
| 1, `/grid?grid=caiso` at 390 px | 539 of 390 px | 390 of 390 px; the reliability table 526 px wide inside its 358 px frame; its 226 empty cells still read "none" |
| 3, `/conditions`, CAISO over the September 2022 heat wave | "(44)" over 40 rows, the last of 8 September | "(44)" over 44 rows, the last "2022-09-09 RMO 12:00 to 22:00" |
| 3, the same over the August 2020 heat wave, beside SPP | "(79)" over 40 rows, the last of 17 August | "(79)" over 79 rows, the last of 24 August; the page 390 of 390 px with them |
| 3, the line under an operator's name | "days and hours in America/Los_Angeles clock time for days and hours" | "America/Los_Angeles clock time for days and hours" |
| 2, `/events/covid-2020` at 390 px with every table shown | 392 of 390 px | 390 of 390 px |
| 2, `/curtailment/where-when`, the trend's table | "CAISO, the whole system: curtailment, GWh" over solar alone | "CAISO, the whole system: solar curtailed, GWh" |

Picture: `docs/reviews/browser-read-2026-11-26/grid-caiso-reliability/reliability-390-after-the-landing.png` (CAISO's reliability section at 390 px after the landing).

**The pages whose words the landing changed** (the old laptop's audit fixes on `/curtailment`, `/datacenters`, the queues, `/severance`, `/storage`, the Grid tool's tabs and `/cost-of-power`), after it: the site's own figure check on their 106 addresses, 6,680 of 6,680 match Supabase (14:41 UTC); eighteen of them at 1280 and 390 px as they open and with every table shown (`runs/c750/quiet_tables.mjs`): no quiet fault but CP1, which is filed and still there (`/cost-of-power?view=grids`, 1,677 px at 390 px with its hour-of-day table shown).

### `/impact` with Datacenter (window C's, chain 740: read, never edited)

**The four plant types show the figures they showed before.** Every marked figure of sixteen addresses of `/impact` was saved while production still drew the earlier build, and again after it drew the new one (`runs/c750/c_impact_figs.mjs`). The deploy came in the middle of the first pass, so eleven addresses were truly read before (land-based wind in three states and as the page opens, utility solar in four, natural gas in three) and five after. On those eleven: 1,700 figures, each with the same key, the same raw value and the same words after as before; the page's sentences the same; the count of "not held" the same. None differs, none is gone. Geothermal was not caught before the deploy; its figures that earlier browser reads wrote down are on the page as they were (Nevada, 36 MW: property tax, first operating year USD 876,642; Nevada, 26.5 MW: taxes, present value USD 0 with its blanks). So are the opening page's (construction jobs 515, operating jobs 44.7, construction earnings USD 41 million, sales and use tax USD 19.9 million, earnings present value USD 83.6 million), Wyoming's wind (property tax over the life USD 36.2 million) and Minnesota's (689 job-years).

**The Datacenter part, read in full at 1280 and 390 px** (14:25 to 14:36 UTC; `runs/c750/c_impact_dc3.mjs` to `c_impact_dc6.mjs`, `c_impact_tracker.mjs`).

*Five cases, written first, then taken on the page.*

1. *A county commissioner in Texas:* what would a 1,000 MW datacenter bring? The page opens on it: 5,500 construction jobs, 306 permanent jobs, USD 411.2 million of construction earnings, USD 2.46 billion of sales and use tax over the life. Property tax is blank until the reader types the county's rates, and says so. Answered.
2. *An economic developer in Virginia:* what does the state's exemption cost? Virginia chosen: sales and use tax before the exemption USD 1.73 billion, forgone by it USD 865.7 million, paid USD 865.7 million; jobs with the state's own study's ratios (9,250 construction, 1,037 operating). Answered.
3. *A journalist checking an announcement:* Meta's expanded Richland Parish campus picked from Louisiana's list: 5,000 MW, USD 50,000 million, 1,000 permanent jobs and 7,500 construction workers, each the document's, and "the document" opens Louisiana Economic Development's release of 13 July 2026. Louisiana's exemption forgoes all USD 3.04 billion of the default's sales tax. Answered.
4. *A skeptic:* what do the totals leave out? Each missing part is a blank with its reason; the total itself does not say (row I2).
5. *A reader on a phone:* the page is 390 px wide as it opens, with a project picked and with every table shown and fold open; each chart gives a card under a finger; all 53 marks open inside the screen.

*Figures.* All 25 announced projects of `site/data/forecast/datacenter_announced.json` picked in their ten states: each sets the megawatts, the permanent jobs and the construction workers its document states (a figure the document does not state keeps its default), and the investment in 2025 dollars (a 2024 announcement times 1.026, 2023 times 1.053, 2021 times 1.170, 2018 times 1.260; a 2025 or 2026 one as stated). Each names its document and links it: 25 of 25. The address the page writes after a pick, opened fresh, shows the same figures at both widths (three projects). Six states' A and B tables read row by row: Texas, Ohio and Wyoming (no exemption read: blank, with the reason), Virginia (half the sales tax forgone), Louisiana (all of it), Georgia (row I3).

*A part with no public source is blank with its reason,* each read on the screen: construction and operating output ("not computed for a datacenter"); property tax ("no property tax rate is held statewide: the reader's rates are not given"); the tax forgone by the exemption ("no datacenter sales tax exemption of this state has been read"); the tax on the electricity bought ("no statute on the electricity bought is read for this state"); the building's taxable purchases ("No public document read gives it for a datacenter: not given, and the building's sales tax is left out until the reader types one"). Severance reads "none" ("a datacenter burns no gas"), which is a true none.

*The hand and the quiet faults.* Each of the three charts answers the mouse and a finger (4 of 4 places); the keyboard reaches the foot in 93 stops, each seen and marked; no sideways scroll, no empty chart, no "undefined", one h1 and no skipped level; opens in 1.2 s. A choice replaces the address and adds no step for the back button, as the tool's four plant types do.

*The same number in two places.* None of the 25 announced projects is named on the tracker's pages (`/datacenters`, its By grid view, the project map), so no megawatt stands in both places to be set side by side, and nothing contradicts. A reader cannot go from Meta's 5,000 MW here to a row of the tracker; the tracker's facilities from the news are held for a license.

| # | Done | Seen | Should be seen | Whose |
|---|---|---|---|---|
| I1 | Each of the 29 assumptions' marks read one by one, a press elsewhere closing each | 17 name the document their default comes from, with its page and often its words (JLARC's "Data Centers in Virginia 2024", page 14 and Table D-1; Census County Business Patterns 2023; OMB Circular A-94; Louisiana's R.S. 47:305.73); 6 say the figure is a choice or the reader's own. None holds a link, and the page's five links that leave the site are to none of these | The chain's test for this page: every default opens its document. The announced projects' documents do open (25 of 25); JLARC's report, the Census table, the circular and the statute are named and cannot be opened from the page | window C |
| I2 | Texas as it opens; the row "Taxes, present value" and its mark | USD 1.45 billion. Its mark says the total is "property, sales and use paid, income and electricity taxes". In this run property tax and the electricity tax are "not held" two and six rows away; nothing on the total's row or in its mark says they are not in it. (The chart of other states does say it of itself: "Property tax is left out") | The total saying what it leaves out in this run | window C |
| I3 | Georgia chosen; the row "Sales and use tax forgone by the exemption" | "none", with the hover "the state's relief is held as words only, not applied: its hover says why (an approval, or a threshold not read)". On a phone, or without the hover, the page says Georgia's exemption forgoes nothing | "not held" with that reason, as the states with no statute read; "none" stays for severance, which is none | window C |
| I4 | Brookfield's Paducah campus picked (Kentucky); Starwood's Mason County campus (West Virginia) | Paducah: the investment stays at the default, USD 19,800 million, beside a linked document that says "more than $100 billion". Starwood: permanent jobs stay at the default, 661.2, beside a document that says "approximately 1,500 jobs". The file's own notes give the reasons (the USD 100 billion holds 2 GW of gas and batteries; the 1,500 jobs are not said to be permanent or construction). The page says neither | One line by the list when a document's figure is not taken, with the note's reason | window C |
| I5 | A hand-made address with the project alone: `/impact?tech=datacenter&state=la&dcproj=la_meta_richland_2026` | The list shows the campus picked and its document linked; the fields hold the default (1,000 MW, USD 11,000 million, 306.1 jobs) and the table 5,500 construction jobs, under the name of a 5,000 MW campus | The project's figures, or the list on "None" | window C; small: the address the page itself writes carries the figures and opens right |

Also seen, and not this page's: the shared "About" mark does not close on Escape (known since the tooling pass of 20 October), and an open box covers the mark of the row under it, so the next mark answers only after a press elsewhere.

Pictures: `docs/reviews/browser-read-2026-11-26/impact-datacenter/impact-datacenter-as-it-opens-1280.png` (Texas, 1,000 MW); `docs/reviews/browser-read-2026-11-26/impact-datacenter/impact-datacenter-an-announced-project-1280.png` (its most telling choice: an announced project picked in Louisiana); `docs/reviews/browser-read-2026-11-26/impact-datacenter/impact-datacenter-virginia-1280.png` (Virginia, the exemption's cost).

### Before `/equities` lands: its energy prices against the price board

The equities page files reached main at 12:51 UTC (`site/data/equities/`, built 12:14 UTC; the equity side held, eight energy prices shown); the page had not landed at 14:54 UTC. The same number in two places was read from the file and from the board as production drew it at 14:53 UTC (`runs/c750/c_board_capture.mjs`, `c_equities_vs_board.py`):

| Series of the equities file | The file's latest | The price board |
|---|---|---|
| WTI crude oil, Cushing, spot | 89.53 on 17 November | 89.53 USD/bbl, 17 Nov |
| Brent crude oil, Europe, spot | 92.94 on 17 November | 92.94 USD/bbl, 17 Nov |
| Henry Hub natural gas, spot | 3.10 on 17 November | 3.10 USD/MMBtu, 17 Nov |
| ERCOT Hub average, day-ahead, daily mean | 46.3104 on 25 November | 46.31 USD/MWh, 25 Nov |
| CAISO SP15, day-ahead, daily mean | 38.8894 on 25 November | 38.89 USD/MWh, 25 Nov |
| CAISO NP15, day-ahead, daily mean | 48.6138 on 25 November | 48.61, 25 Nov (the week's table) |
| Uranium, monthly average | 72.8876 for October 2026 | 72.89 USD/lb, Oct 2026 |
| California carbon allowance, current auction | 32.48 for August 2026 | 32.48 USD/t CO2e, Aug 2026 |

Eight of eight agree, value and day. The four series the file holds back carry no value in it, each with its reason (PJM Western Hub, NYISO New York City and ISO-NE Mass Hub "license needed", MISO Indiana Hub "paused"); the board draws the same hubs blank ("licensed source needed", "license needed"). The board itself is recorded as it stood (25 groups, 276 rows, 12 tiles), to be set beside the board once the equities group lands.

## For Samuel's ruling (each with the page left as it is)

1. **A reason on hover and a finger.** Why a strip or a cell is blank, why two figures differ, and what a colored cell holds are given as the browser's own tooltip. A mouse opens it; a finger at 390 px opens nothing. Seen on `/conditions` (the blank strips), `/congestion` (the hour-by-month cells, the operators not drawn), `/demand`, `/supply` and `/events` (blank cells and the figures' notes). The "i" marks and the chart cards do open on a tap. Default taken: nothing changed. The question: should a blank's reason open on a tap, as the "i" marks do?
2. **`/congestion`, a thousands comma.** The lists print "1080.08 USD/MWh" beside "330,132". The gate's own check (`check-values`) pins USD/MWh "without a thousands comma". Default: left.
3. **`/congestion`, "contingency Base Case".** CAISO's base case is printed as a contingency ("HUMBOLDT_IMP_NG (contingency Base Case)"); SPP's base case has no suffix. Default: left, as the operator's own word.
4. **`/supply`, a year with a month left out.** The mix table is 1,325 px wide inside its frame (900 px otherwise), because "not held yet" does not wrap; on a phone two columns show at a time. The page itself keeps to 390 px. Default: left.
5. **The tour's Digest stop** still quotes two headings the Digest page does not show ("Top of the industry", "ERW's Numbers Today"); the tour's check passes 101 of 103 for it. Standing since 20 November. Default: left.
6. **`/conditions`, the alerts list.** On the branch every notice is a row (79 rows for CAISO's August 2020 heat wave). If the list should stay at 40, the page should say that it is cut and where it stops; one line either way.
10. **The Grid tool's Network view, the address while a story plays.** The page tells its reader to copy the address to share the view. While a Watch story plays, the address is still the live week's; it takes the story once it is paused. Default: left. The choice: write the story into the address when it is pressed (and the hour when paused), or say "pause, then copy".
11. **The Price years list and the back button, two pages two ways.** On the battery tool (and every setting of its box) a choice is written over the page's place in the history, so one step back leaves the tool; on the generator's page the same list adds a step, so one step back undoes the choice. Default: left, each as its code says. The choice: one way for the economics pages.
9. **The All grids tab and the keyboard.** A reader with the keyboard alone passes more than 500 stops before the foot of `/cost-of-power?view=allgrids`: every row's marks are stops. Default: left.
8. **`/research`, "hover reads them".** The six small example charts give no value under the mouse or a finger, by design, and the line above them says they do. Default: left (the old laptop audits Automated Analysis tonight; row R1 names it). The choice: take the words out, or give the small examples their values.
7. **"not held" in a chart's table, with no reason.** A chart switched to its table prints "not held" for a missing value and gives no reason on hover (1,206 blanks on the 22 pages of B12 and B14). The tables the pages draw themselves do give one. Default: left; the shared chart table does not know why a value is missing.
