# The browser read of 26 November 2026: everything landed since 20 November, and what lands tonight

Energy Research Warehouse (ERW). Chain 750 (`queue/done/750-night-26-november-portable-window2-browser-read.md`), the portable laptop's second window, sessions 11000 on. Every page is read on production (`https://erw-flame.vercel.app`) in the internal view, in the laptop's own Chrome driven by `site/scripts/browser.mjs`, at 1280 px with a mouse and at 390 px with a finger (touch events). No build is made here and no model is called. The scripts are in `runs/c750/` on the laptop (not in git); the pictures are in `docs/reviews/browser-read-2026-11-26/`.

How a row reads: what was done, what was seen, what should be seen, and whose it is. A site fault on a page no window owns tonight is fixed on a branch `wip/c750-<page>` with a test and is a row of `docs/state/landing_request_portable_w2.md`. A fault on a page another window owns tonight is a row here that names the window, and its code is not edited. A data fault is a row of `docs/state/data_requests_done_line.md`. A thing that is a choice is one line under "For Samuel's ruling" at the foot, with the page left as it is.

## Where things stand (kept current)

| | Count | Where |
|---|---:|---|
| Pages and views read in part B's form | 14 of the list's 14 begun; see each section | below |
| Faults fixed on a branch, to be seen in a build | 3 (G1, C1, C2) | `wip/c750-grid-reliability`, `wip/c750-conditions`; rows 1 and 3 of `docs/state/landing_request_portable_w2.md` |
| Faults filed for another window | 1 (two unlanded commits, L1) | row 2 of the same file |
| Known to their owner, read again when repaired | 1 (the page files of 21 to 25 November, L2) | chain 701, part C |
| For Samuel's ruling, the page left as it is | see the foot of this file | "For Samuel's ruling" |

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

## For Samuel's ruling (each with the page left as it is)

1. **A reason on hover and a finger.** Why a strip or a cell is blank, why two figures differ, and what a colored cell holds are given as the browser's own tooltip. A mouse opens it; a finger at 390 px opens nothing. Seen on `/conditions` (the blank strips), `/congestion` (the hour-by-month cells, the operators not drawn), `/demand`, `/supply` and `/events` (blank cells and the figures' notes). The "i" marks and the chart cards do open on a tap. Default taken: nothing changed. The question: should a blank's reason open on a tap, as the "i" marks do?
2. **`/congestion`, a thousands comma.** The lists print "1080.08 USD/MWh" beside "330,132". The gate's own check (`check-values`) pins USD/MWh "without a thousands comma". Default: left.
3. **`/congestion`, "contingency Base Case".** CAISO's base case is printed as a contingency ("HUMBOLDT_IMP_NG (contingency Base Case)"); SPP's base case has no suffix. Default: left, as the operator's own word.
4. **`/supply`, a year with a month left out.** The mix table is 1,325 px wide inside its frame (900 px otherwise), because "not held yet" does not wrap; on a phone two columns show at a time. The page itself keeps to 390 px. Default: left.
5. **The tour's Digest stop** still quotes two headings the Digest page does not show ("Top of the industry", "ERW's Numbers Today"); the tour's check passes 101 of 103 for it. Standing since 20 November. Default: left.
6. **`/conditions`, the alerts list.** On the branch every notice is a row (79 rows for CAISO's August 2020 heat wave). If the list should stay at 40, the page should say that it is cut and where it stops; one line either way.
