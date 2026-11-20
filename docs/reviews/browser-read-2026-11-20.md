# The week's pages read in a real browser, 20 November 2026

Energy Research Warehouse (ERW). Chain 620 (`queue/done/620-night-20-november-portable-browser-read-everything-new.md`), the portable laptop, sessions 9600 on. Every page and view landed since 17 November, read on production (`https://erw-flame.vercel.app`) in the internal view, in a headless browser of this laptop, at 1280 px with a mouse and at 390 px with a finger's screen. Nothing was built to read a page; a build is made only to see a fix. Model spend USD 0.

How to read this file: the list first, then one section a page. In a section: the cases a reader would bring, the figures set beside their page file, what answers to the hand, the quiet faults, then the numbered rows (what was done, what was seen, what should be seen) and the pictures. A row's state is `fixed` (with its branch and its landing row), `filed` (a data request, with its number), `ruling` (a choice left as it is, for Samuel) or `noted`.

The scripts are in `runs/c620/` on this laptop (not in git); each row names the one that read it.

## The list

Built from the notes of chains 501, 503, 504, 505, 507, 581 and 590, the progress files, the landing request files, `docs/state/browser_reads_wanted.md` and main's own history of `site/app/` since 17 November. "Seen before" is what a file says a real browser saw before tonight. The pages no browser had seen come first.

| # | Address | What it is | Built by | Seen before tonight | Reads |
|---:|---|---|---|---|---|
| 1 | `/internal/findings` | The findings review page: each draft with its audit, the sheet of forty first | old laptop, chain 507; drafts by the desktop's second window, chain 502 | no (rows 423 to 428 wanted) | `site/data/findings_audit.json`; `scanner_drafts` |
| 2 | `/learn/problems` and the four whole-country sets (`who-trades-with-whom`, `storm-across-the-country`, `under-the-ground-and-in-the-wind`, `where-energy-goes`), each with `data.csv` | Problem sets on the regions, the storms, the resource map and industry | old laptop, chain 507 | no (rows 431 to 436 wanted) | `site/data/regions/trade/`, `trade_matrix.json`, `regions/events/`, `resources/manifest.json`, `industry.json` |
| 3 | `/learn/problems/<set>/2026-11-20` and `/teacher` | The dated edition: ten sets, 59 questions | data machine, chain 581 | no | `site/data/problem_editions/2026-11-20.json` |
| 4 | `/tour/8` to `/tour/15` | Eight new stops of the tour | old laptop, chains 507 and 590; data machine | `/tour` only | `site/lib/tour.ts` |
| 5 | `/map?tab=resources`, the hover of the wind sites and the hot-water systems | Plain words and units in the hover | portable, chain 504; file by the data machine | no | `site/data/resources/hover_fields_added.json` |
| 6 | `/queues/places` | Queues outside the seven grids, by owner and state | data machine, chain 581 | by a script; no width named | `site/data/queue_places.json` |
| 7 | `/curtailment/where-when` | Where and when power is spare, hour by month | data machine, chain 581 | "read on production"; no width named | `site/data/curtailment/where_when.json` |
| 8 | `/board`, the group "Uranium and battery metals, monthly" | Four new rows: aluminum, zinc, lead, tin | data machine, chain 581 | "read on production"; no width named | `site/data/board.json` |
| 9 | `/storage/places` | Batteries by authority and state, two side by side | data machine, chain 581 | at 390 px only | `site/data/storage/places.json` |
| 10 | `/map`, Projects, "Lines on the map" | Transmission of 230 kV and above; HGL pipelines | data machine, chain 581 | at 1280 px only | `site/data/map_layers/` |
| 11 | `/learn/problems/your-own-balancing-authority` | The fifth new set (TVA) | old laptop, chain 590 | row 437 wanted; the landing row says read at both widths | `site/data/regions/authority/tva.json`, `erco.json`, `ciso.json` |
| 12 | `/grid?grid=us48&view=network&shape=map`, the Price control | The map colored by price, eight measures | data machine, chain 505 | on production at both widths | `site/data/regions/prices_map.json` |
| 13 | the same map or the network, a click on an authority | The panel's block "Its own facts" | data machine, chain 505 | on production at both widths | `site/data/regions/authority/<code>.json` |
| 14 | `/states` | Every state, two side by side | data machine, chain 581 | at both widths | `site/data/states/` |
| 15 | `/industry` | Energy use by industry, fuel and state | data machine, chain 505 | at both widths | `site/data/industry.json` |
| 16 | `/ai-energy` | Energy per AI query, as published | data machine, chain 505 | on production at both widths | `site/data/ai_energy.json` |
| 17 | `/demand?view=country#forecast` | The forecast beside what happened | data machine, chain 505 | the view yes; the section not named | `site/data/regions/forecast/` |
| 18 | `/demand?view=country` | The whole country: any two of 13 regions and 58 authorities | old laptop, chain 503 | yes (portable, chain 504); two rows fault, two wanted | `site/data/regions/demand/` |
| 19 | `/supply#whole-country` | Net imports, who trades with whom, the mix by region | old laptop, chain 503 | yes; two rows wanted | `site/data/regions/trade/`, `mix/`, `trade_matrix.json` |
| 20 | `/events` and `/events/<event>#whole-country` | The thirteen regions across each of nine events | old laptop, chain 503 | yes; one row wanted | `site/data/regions/events/` |
| 21 | `/grid?grid=us48&view=network&shape=map` | The map of the balancing authorities | portable, chain 504 | yes, with a finger at 390 px | `site/data/regions/ba_boundaries.json`; the hourly snapshot |
| 22 | `/grid?region=<code>` | The thirteen regions in the Grid tool | portable, chain 504 | yes | `site/data/regions/index.json`, `mix/`, `trade/` |
| 23 | `/map?tab=resources` | The resource map, with the coal fields | portable, chain 504; layers by the data machine | yes, finger and keyboard | `site/data/resources/` |
| 24 | `/grid?grid=us48&view=network` | The 3D network, opening on the hour its slider names | portable, chain 504 | yes | the hourly snapshot |
| 25 | `/map`, Projects | Proposed in-service dates restored | data machine, chain 505 | yes | `site/data/map.json` |
| 26 | `/data/methods/ba_boundaries` | A new method page | data machine, chain 501 | yes | `docs/methods/` |

Not on main, so not read: `/congestion` and `/conditions` (the data machine's chain 601, building tonight) and the variables table on the pages under `/data/methods/` (the desktop's second window, chain 630). Each is read in part E once it lands; none is edited here.

Not on production though a landing row says so: the old laptop's sessions 8470, 8480 and 8490 (the last fixes to items 18, 19 and 20). See the note at the foot of `docs/state/landing_request_oldlaptop.md`.

## The first pass: every page as it opens

Each address opened at 1280 and at 390 px on 20 November about 10:50 UTC (`runs/c620/survey.mjs`, `runs/c620/b1.out`). For every page: no sideways scroll at 390 px, no "undefined", "NaN" or "null" on the screen, no chart with nothing in it, no error in the page. The slowest to its load event: `/supply` 2.1 s, `/demand?view=country` 1.6 s, `/map` 1.5 s, `/events/elliott-2022` 1.5 s at 390 px; every other page under 1.1 s. `/internal/findings` takes 4.6 s (item 1).

## Found on more than one page

Rows here are counted once; a page's section points at them.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| S1 | On a page with lists that submit themselves (`/queues/places`, `/curtailment/where-when`, and every page that draws the shared list of `site/components/AutoSubmit.tsx`): two choices made one after the other, then the browser's back button | The address and the page go back one choice; the list keeps the later choice. On `/queues/places` after TVA then Duke: the address reads `b=West:PacifiCorp`, the table shows PacifiCorp, the list "Queue B" reads Duke. On `/curtailment/where-when`: the grid shows 2025, the Year list reads 2019 | The list reads what the page shows | fixed on `wip/9601-back-button-lists` (the browser puts a form's last state back between a page's load and its showing; the list is now set to the page's value when the page is shown). `site/scripts/check-back-button.mjs` fails on production on all four pages it reads (4 of 16) |
| S2 | A figure that is given only on hover, pressed with a finger at 390 px and reached with the Tab key | Nothing: the figure is the browser's own tooltip (a `title`). On `/curtailment/where-when` this is every figure of the hour by month grid (288 cells, none reachable by the keyboard, none shown to a finger); on the problem sets it is each figure's page file | A choice, not a fault of one page: it is ruling 13 of chain 504's note (should a reason also open on a tap? default: left as the site has it) | ruling (see "For Samuel's ruling") |

## The fixes, and what has been seen of them

Ten branches, each cut from origin/main with its test, pushed. **None has been seen in a build:** this laptop had 1.0 to 1.8 GB of memory free from 11:37 UTC on (Samuel's own Chrome and the Claude programs hold the rest), under the 2 GB the chain asks for a build, and the whole suite was not run for the same cause. So no landing is requested yet (`docs/state/landing_request_portable.md`, rows 44 to 53, state "ready, not requested"). What was seen without a build is said on each line.

| Branch | Head | What it mends | Its test | Seen so far |
|---|---|---|---|---|
| `wip/9601-back-button-lists` | `dc046acff` | Row S1: the shared list after the back button | `tests/test_session9601_back_button.py` (7), with the two older tests that name the list: 32 pass; `site/scripts/check-back-button.mjs` | The check fails on production (4 of 16). In a real browser on a plain page of two lists (`runs/c620/backtest.mjs`): without the mend the list reads the later choice on the page shown again; with the same logic it reads the page's value. The browser puts the state back after the page's load and before its showing. On production's own pages with the mend's logic put into each page as it loads (`runs/c620/back_button_emulated.mjs`): 6 of 6 pages keep their lists true after back and forward (`/queues/places`, `/storage/places`, `/curtailment/where-when`, `/ai-energy`, `/states`, `/industry`); as production is, 0 of 6 |
| `wip/9601-findings-phone` | `4971346fa` | `/internal/findings` at 390 px | `tests/test_session9601_findings_phone.py` (3), with session 233's: 36 pass | The branch's one style applied to production's page in the browser: 390 px wide (was 470) |
| `wip/9601-resource-set-legend` | `9632634e5` | The resource set's legend | `tests/test_session9601_resource_set_legend.py` (9); the replication 0 of 142 differ | Not seen in a browser. One older test fails on this branch and on main alike (`test_session8901_problem_sets_country.py`, "FAIL 16": it expects no dated edition, and the edition of 20 November exists) |
| `wip/9601-authority-facts-words` | `225e96ed8` | "Net imports met -592 percent of its demand" | `tests/test_session9601_authority_facts_words.py` (5), with the panel's: 10 pass | Not seen in a browser |
| `wip/9601-tour-headings` | `bff5d765a` | The tour's stops 1, 4, 11 and 12 | `tests/test_session9601_tour_headings.py` (7), with the tour's four older tests: 27 pass; the tour's render test passes | The branch's stops and check run against production's pages: 94 of 97 pass (89 of 96 before). The three left: the Digest stop's two headings (for a ruling) and the tour's own fourth page, which still links `/grid` until the branch lands |
| `wip/9601-policy-held-page` | `e029f90aa` | `/policy` when its list is held | `tests/test_session9601_policy_held_page.py` (6), with the seven older tests that name the page: 90 pass | Not seen in a browser |
| `wip/9601-price-map-window` | `58d119d6d` | The Grid map's price over a window names its days | `tests/test_session9601_price_map_window.py` (6), with the map's: 13 pass | Not seen in a browser |
| `wip/9601-line-ends-unnamed` | `5416bba3e` | A transmission line's end that HIFLD marks "UNKNOWN<number>" | `tests/test_session9601_line_ends_unnamed.py` (4), with the layers': 11 pass | Not seen in a browser |
| `wip/9601-method-pages-phone` | `c6263da57` | Six method pages that scroll sideways at 390 px | `tests/test_session9601_method_pages_phone.py` (5), with the four older tests that name the stylesheet: 48 pass | The branch's one rule put on production's six pages in the browser: each 390 px wide (they were 392 to 544), tables unchanged, two pages that fitted unchanged |

### Seen in a build, on the desktop (the second window, session 9203, 19:20 to 19:40 UTC)

The chain passed to the desktop's second window when the portable laptop stood down. The ten branches (the nine above and `wip/9602-faults-page-phone`) were merged one after another onto main at `7d3a0797d` as `wip/w2-c620-fixes` (`28a564722`), with no conflict; built under `scripts/buildlock.py` (68 s, 7.7 GB of memory free); served on port 3620 and read in the internal view at 1280 and 390 px; the server then stopped. **Landing requested as one row:** row 4 of `docs/state/landing_request_window2.md`.

| Fix | What the build shows | State |
|---|---|---|
| The back button and the lists | `site/scripts/check-back-button.mjs`: 16 of 16 (production fails 4) | seen fixed |
| The tour's stale headings | `site/scripts/check-tour.mjs`: 101 of 103 over sixteen stops; the two that fail are the Digest stop's headings (row D4, a ruling) | seen fixed |
| `/internal/findings` at 390 px | 390 px wide | seen fixed |
| Six method pages at 390 px | `/data/methods/resources` and `interconnection_queue_summary` 390 px wide (were 544 and 421) | seen fixed |
| `/data/faults` at 390 px | 390 px wide (was 417) | seen fixed |
| `/policy` | The heading "Policy", links to its two views, "license needed" where the list would be | seen fixed |
| The resource set's legend | 1.58 to 6.91 on the set's page; 2.81 no longer on it | seen fixed |
| Seminole Electric's panel | "It sent out, net, power equal to 592 percent of its demand." at 1280 and 390 px | seen fixed |
| The map's price over twelve months | ERCOT: "34.86 USD/MWh at HB_HUBAVG, day-ahead, the 365 days to 2026-11-16" at both widths | seen fixed |
| A line's end HIFLD does not name | "an end HIFLD does not name (its mark UNKNOWN202693) to GREAT FALLS (RAINBOW)"; of six line tips read, none prints a bare UNKNOWN mark as a place | seen fixed |

Tests on the head, with `site/node_modules` installed: the 52 test files that name a changed file, 544 passed, 10 skipped, 2 failed (`test_session7534_problem_sets`, `test_session8901_problem_sets_country`), both failing the same way on main. Script: `runs/c620w2/see_fixes.mjs` (this window's folder, not in git).

Pictures: `docs/reviews/browser-read-2026-11-20/fixes-seen-in-a-build/`: `findings-390.png`, `method-resources-390.png`, `faults-390.png` (each page at a phone's width, nothing past the edge); `policy-1280.png` (the Policy page with its heading and views); `resource-set-1280.png` (the set with the new legend figures); `grid-seminole-facts-1280.png` (Seminole's own facts, the new sentence); `grid-price-twelve-months-ercot-1280.png` (ERCOT's card naming its 365 days); `map-line-unnamed-end-1280.png` (a line's tip with an unnamed end).

## 1. `/internal/findings`: the findings review page

Read for rows 423 to 428 of `docs/state/browser_reads_wanted.md` (`runs/c620/a2_findings.mjs`). No ruling button was pressed.

- **Seen:** the sheet of forty opens first, none drawn twice; the first block has its reader, title, sentence, figure, comparison, what would make it wrong, the audit's verdict, the four checks, the tables and the Stata and Python links; the chart's picture is drawn; the do-file opens in place and its "save" gives the repository's file under its own name; the bar of counts stays at the top while scrolling; each filter narrows; the search "Dominion" finds 3; "Show the next 40" adds forty; a withdrawn draft and a not-checked draft draw Approve disabled with the reason.
- **Time:** 4.6 s to the load event at 1280 px, 4.2 s at 390 px (614 drafts drawn by the server, 241,575 characters). Inside five seconds on this laptop, and the slowest page of the week.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | The page at 390 px | The page is 470 px wide: it scrolls sideways. A hunt's caption draft (a box of session 233) holds a long word that does not break | 390 px | fixed on `wip/9601-findings-phone`. With the branch's one style put on production's page in the browser, the page is 390 px wide |

## 2. The four whole-country problem sets, and 11. the fifth (`your-own-balancing-authority`)

Read for rows 431 to 437 (`runs/c620/a2_sets.mjs`): every answer opened at both widths.

- **Seen:** each figure the rows name is on the page at 1280 and 390 px; each of the 503 figures of the five sets names its page file and path on hover; each set's `data.csv` answers with one row a figure; the index lists ten sets, each with the edition of 20 November; no sideways scroll with every answer open.
- **Against the pages the sets send a student to:** Elliott's page gives Tennessee the same highest hour (33,225 MW at 2022-12-24 01:00 UTC) and baseline (19,830 MW) as the storm set.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | "What is under the ground and in the wind", the worked example: "switch on Global Horizontal Irradiance; the legend runs from its lowest to its highest value", then the legend on `/map?tab=resources` | The set: lowest 2.81, highest 6.50 kWh/m2/day, 2.32 times. The map's legend: 1.6 to 6.9. The map widens a layer's legend to hold Alaska's and Hawaii's parts; the set reads the contiguous states' range from the list of layers. Question 2 uses the same 6.50 | The set and the map give a student the same two numbers | fixed on `wip/9601-resource-set-legend`: the set reads each end of the legend over every part of the layer, as the map does (1.58 to 6.91, 4.36 times; question 2: 9 over 6.91, 1.30 times), each figure naming the part it is read from; the replication reads it the same way, 0 of 142 differ. The dated edition of 20 November keeps the old figures: data request 567 |
| 2 | The same set, question 3: the wind legend's top | The set: 13.58 m/s. The map's legend: 13.6 (one decimal) | The same figure; the legend rounds | noted |

## 3. The dated edition of 20 November 2026

The data machine's file (chain 581), drawn by the old laptop's pages. Read with `runs/c620/b_edition.mjs`: the students' copy and the teacher's copy of each of the ten sets, at both widths.

- **Seen:** twenty pages, each with its heading, no "undefined", no sideways scroll, the slowest 0.6 s. Each students' copy holds its questions and no answer; each teacher's copy holds an answer for every question (59 questions over the ten sets).
- **Figures:** every figure the edition's file holds for a set (198 distinct figures over the ten) is on the teacher's copy at the screen's decimals; none missing.
- **A figure the map contradicts:** the edition's resource set gives the sun's legend as 2.81 to 6.50; the map shows 1.6 to 6.9 (item 2, row 1). An edition keeps its day's numbers: data request 567 asks for a new edition once the mend lands.

Pictures: `docs/reviews/browser-read-2026-11-20/edition/students-copy-1280.png`; `teachers-copy-1280.png` (the same set with its answers).

## 4. The tour's new stops, and 18 to 26. The pages already read once, opened again

Read with `runs/c620/b_sweep.mjs`: 101 addresses at 1280 and at 390 px, for what breaks a page quietly. The thirteen regions in the Grid tool (each region's Network, Mix and Clean tab), the Grid tool's four other openings, the nine events with two regions chosen, `/demand?view=country` and `/supply` for thirteen pairs of regions each, the resource map, the project map, two method pages, the tour and its fifteen stops.

- **At 1280 px:** 101 opened, each its own page, no sideways scroll, no "undefined", "NaN" or "null", no empty chart, no error. One took 5.0 s the first time it was asked for (`/events/covid-2020` with two regions; 1.0 to 2.7 s on five more loads): a page not yet in the server's cache.
- **At 390 px:** 101 opened; one scrolls sideways (row 1). The slowest 2.8 s.
- **Not done again tonight for these pages:** the five cases and the figure by figure read. Chain 504 took them for the map, the regions and the resource map (`docs/reviews/grid-map-read-2026-11-19.md`), and the old laptop for the events, demand and supply pages; the old laptop's last fixes to those three are not on production (the note above the first pass).

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | `/data/methods/resources` at 390 px, then all 609 method pages at 390 px (`runs/c620/b_methods_wide.mjs`) | Six scroll sideways, each over one long unbroken word of the note's text: `resources` 544 px (a 61-character file name), `interconnection_queue_summary` 421, `amm_guatemala_generation_monthly` 417, `ercot_dam_esr_awards` 411, `makstat_macedonia_electricity_monthly` 401, `statcan_oil_gas_supply_monthly` 392 | 390 px | fixed on `wip/9601-method-pages-phone` (one rule of the prose style) |
| 2 | `/internal/findings`, its size | 17.1 MB of HTML for 614 drafts, of which forty are shown at a time; 3.7 to 4.1 s to load over five loads | Inside five seconds on this laptop; heavy for a phone. An internal page | noted |

### The tour's stops 8 to 16 walked as a reader (the desktop's second window, session 9203)

`runs/c620w2/b_tour.mjs`, on production at 1280 and 390 px, about 19:45 UTC: each stop's page (its bar, Back, Next and its Open link), then the page it opens, timed, with its quiet faults, every heading the stop quotes looked for, and the stop's own action done as its words say. **75 of 77 checks pass.** Each stop opens in 0.1 to 0.5 s and each page it opens in under 4 s (`/grid` 3.9 s the first time at 1280 px, 1.3 s at 390 px); none scrolls sideways or shows "undefined", "NaN" or "null"; stop 16's "choose Winter Storm Uri under Event" works at both widths (`/conditions?a=ercot&b=none&event=uri_2021`).

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 3 | Stop 8, as its words say: "Pick Tennessee ... in the region list at the top; open its network view for the map" | Tennessee is a link of the "EIA region" row (`/grid?region=ten`); its Network tab opens on the 3D network, with no area of the map drawn. The map is one more press, on "Map" (`&shape=map`, 60 areas). The network opening first is Samuel's standing ruling; the stop's words never name the press | The stop names the press on Map | fixed on `wip/w2-c620-fixes` (`1d7b451a6`, with `tests/test_session9203_tour_stop8.py`); landing row 4 of `docs/state/landing_request_window2.md` |
| 4 | Stop 8: "then read "Ask" at the foot of the page" | At 1280 px "Ask" is a panel beside the tool, at the top right; it is under the tool only at a phone's width | The words say where it stands at both widths | fixed in the same commit ("beside the tool on a wide screen and under it on a phone") |
| 5 | Stop 12, "How the map is drawn" | Inside the closed fold "Method note" on production | | already fixed on `wip/9601-tour-headings` (row D6), now in `wip/w2-c620-fixes` |

Pictures: `docs/reviews/browser-read-2026-11-20/tour/stop-08-1280.png` to `stop-16-1280.png` (each stop's own page); `stop-08-tennessee-network-1280.png` (where stop 8's words leave a reader: Tennessee's Network tab on the 3D network, the Map button beside it); `stop-09-page-1280.png` to `stop-15-page-1280.png` (the page each stop opens, as it opens); `stop-16-uri-1280.png` (`/conditions` after choosing Winter Storm Uri).

## 6. `/queues/places`: queues outside the seven grids

The data machine's page (chain 581). Read with `runs/c620/b_queues_places.mjs`.

**Five cases.**
1. *A developer choosing between two Northwest queues.* Which is more crowded, BPA or PacifiCorp, and with what? Opens the page: BPA 129,878 MW active against PacifiCorp 49,019; solar with battery leads both (56,798 and 22,595). Answered as the page opens.
2. *A utility planner in the Southeast.* How does TVA's queue compare with Duke's, and how much has each withdrawn? Chooses TVA and Duke: active 23,485 against 30,030 MW, withdrawn 218,498 against 112,624. Answered; the chart shows the year each active entry entered.
3. *A state energy office in Georgia.* What do the queues that name Georgia hold? The states' table: 810 entries, 38,252 MW active, owners GTC, SOCO, TVA. Answered, though the owners are abbreviations (row 1).
4. *An AI lab's siting analyst.* Where outside the seven grids is the most capacity waiting? The states' table by eye: Oregon 103,932 MW, Arizona 83,591. Answered; the table cannot be sorted, so the largest is found by reading down.
5. *A student.* What share of Kentucky is outside the seven grids, and who runs its queue? 82.1%, LGE-KU and TVA. Answered.

**Figures.** Every figure the page marks, as it opens: 370 of 370 agree with `site/data/queue_places.json` (the two owners side by side, the 49 owners' table, the 25 states). After choices (TVA beside Duke; APS beside NVE by a fresh link): all agree. At 390 px: 205 of 205.

**What answers to the hand.** Both lists; the Show button; the chart under the mouse and under a finger (a card at each place tried); the Chart and Table switch; each owner's name (a link that puts it in list A); a link carrying a choice opened fresh; an address that names no owner opens on the first. The keyboard walks 62 stops in the page, each with a focus mark, to the foot. The back button: row S1.

**Quiet faults.** None: 390 px wide at 390, the three wide tables scroll inside their own frames; no empty chart; a blank reads "not held" with its reason on hover. 0.5 s to load.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | Read the owners' names | LBNL's abbreviations with nothing behind them: "S-C", "N-C", "IP", "CLPT", "TSGT", "AEC", "SEC", "BHCT". No hover, no list of names | A reader who does not know LBNL's file cannot tell Santee Cooper from Seminole. A choice (the page says "each under the name LBNL gives its owner") | ruling |
| 2 | The states' table, North Carolina | "APS, Duke, TVA": APS is Arizona Public Service in the rest of the page | Either an entry of LBNL's file that names NC under APS, or a misread state. Not checked against LBNL's file here (this laptop does not hold the table) | filed (data request 562) |
| 3 | Two choices, then back | Row S1 | | to fix (S1) |

Pictures: `docs/reviews/browser-read-2026-11-20/queues-places/as-it-opens-1280.png` (BPA beside PacifiCorp, the page as it opens); `tva-beside-duke-1280.png` (after the choice TVA and Duke, the side by side table).

## 7. `/curtailment/where-when`: where and when power is spare

The data machine's page (chain 581). Read with `runs/c620/b_where_when.mjs`, which recomputes every cell from the page file without the page's code.

**Five cases.**
1. *A battery developer in California.* In which hours and months is solar thrown away? Opens the page: CAISO, solar, 2025, an hour by month grid; the darkest cell is 126,053 MWh. Answered at 1280 px by resting the mouse on a cell; not at 390 px (row 1).
2. *A datacenter's siting analyst.* Where in ERCOT is power priced below zero most often? "The places ranked": the hubs and zones by share of hours below zero in each one's newest whole year, each a link. Answered.
3. *A wind developer in SPP.* How much wind did SPP curtail, month by month? Chooses SPP: the page says SPP publishes by day, not by hour, and gives its months (January 2025: 1,039,118 MWh of wind). Answered.
4. *A trader.* Do West Texas's negative hours fall in the same months as California's curtailment? Chooses CAISO beside ERCOT HB_WEST, every year held: two grids one under the other. Answered at 1280 px.
5. *A student.* Has curtailment grown? "The trend by year" and the table of GWh by whole year: CAISO 2,449.2 (2022) to 3,765.6 (2025). Answered; 2026 reads "not held" with the reason (fewer than 90 percent of the year's days).

**Figures.** As it opens: the 288 cells of CAISO's solar grid for 2025, the 34 figures of the ranked table, the 10 of the GWh table, all agree with `site/data/curtailment/where_when.json`. After choices: wind 2025 (288), wind and solar over every year held (288), ERCOT HB_WEST's share of hours below zero over every year and in 2025 (576, each with its count "n of m hours held"), SPP's 24 months of 2025. 1,536 figures at 1280 px and 291 at 390 px, none differing. Each ranked share is its own count over its own hours, and is the place's own year in the file.

**What answers to the hand.** The four lists; the Show button; both trend charts under the mouse and a finger; the Chart and Table switch; a ranked place's name (opens it in its year). The keyboard walks 32 stops with a focus mark each.

**Quiet faults.** None at open: 390 px wide at 390 (the grid, 760 px, scrolls inside its frame); 0.5 s to load.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | A finger on a cell of the grid at 390 px; the Tab key at 1280 px | No figure comes up; no cell takes the focus (0 of 288). The grid's figures exist only in the browser's tooltip | A phone reader sees shades and no number. Row S2 | ruling (S2) |
| 2 | Wind, then the year 2019, then back | The grid shows 2025; the Year list reads 2019 | Row S1 | to fix (S1) |

Pictures: `docs/reviews/browser-read-2026-11-20/where-when/as-it-opens-1280.png` (CAISO's solar curtailment by hour and month, 2025); `caiso-beside-ercot-west-every-year-1280.png` (CAISO's curtailment over every year held above West Texas's hours below zero).

## 8. `/board`: the four new metals rows

The data machine's rows (chain 581), in the group "Uranium and battery metals, monthly". Read with `runs/c620/b_board_metals.mjs` and `runs/c620/b_board_bench.mjs`.

**Five cases.**
1. *A battery maker's buyer.* What did tin cost last month and how has it moved? Opens the group: Tin 53,712 USD/t, September 2026, down 1,673 (3.0%) on the month, up 19,228 (55.8%) on the year. Answered.
2. *A transmission planner pricing conductor.* Aluminum: 3,283.00 USD/t, up 23.8% on the year. Answered.
3. *An investor.* Where does zinc stand in its year's range? At the top: 4,021 of a range 3,152 to 4,021. Answered.
4. *A student.* Presses Tin: the workbench opens beside the table with the series drawn, its mean, low and high in the window, a CSV and a link to copy; the address becomes `/board?s=wb-pink-tin`. Answered.
5. *A trader looking for a daily price.* Uranium and lithium daily read "licensed source needed", with no figure. Answered: the page says what it does not hold.

**Figures.** Each of the eleven rows of the group against `site/data/board.json`: the latest value, its month, the moves over a month and a year, a small chart in the row. 94 of 94 at 1280 px, 60 of 60 at 390 px. Inside the file, each move is the latest less the earlier value and its percent of the earlier; each row's place in its range is its own.

**What answers to the hand.** The group's heading opens it, by mouse and by a finger; a press on a row opens the workbench with its chart (the tin series' own file holds 801 months), at both widths; the page stays 390 px wide with the group and a row open. The keyboard reaches each row's button.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | Tin's row, then the same row in the workbench with the window "Year" | The row's range over a year: 36,012 to 55,385 (twelve months). The workbench's Year window: low 34,484, high 55,385, 13 values (it holds both ends of the year) | Two lows for "a year" of one series on one screen. A choice of the board's, older than this week | ruling |

Pictures: `docs/reviews/browser-read-2026-11-20/board/as-it-opens-1280.png` (the board as it opens); `metals-group-open-1280.png` (the group open, the eleven rows); `tin-in-the-workbench-1280.png` (after a press on Tin).

## 9. `/storage/places`: batteries in every authority and state

The data machine's page (chain 581). Read with `runs/c620/b_storage_places.mjs`.

**Five cases.**
1. *A battery developer.* How much is operating and planned in ERCOT against CAISO? As the page opens: ERCOT 19,195 MW operating and 24,159 planned; CAISO 17,266 and 10,878. Answered.
2. *A utility planner in Arizona.* How does Arizona Public Service compare with the whole of Texas? Chooses the state Texas and the authority AZPS: side by side, with the planned MW by year. Answered.
3. *A state energy office.* Where does my state rank? "Every state", by operating MW, each name a link that puts the state in list A. Answered.
4. *An investor.* How much of the fleet gives an energy capacity? The row "MW of the units that give MWh" beside "Operating, MW", and the hover on a blank ("No unit here gives an energy capacity"). Answered.
5. *A student.* The country beside California, opened by a link (`/storage/places?a=us&b=st:CA`). Answered.

**Figures.** As it opens, every marked figure: 366 of 366 agree with `site/data/storage/places.json` (the pair, the 43 authorities, the 51 states), and so do Texas beside AZPS and the country beside California. At 390 px: 310 of 310. Inside the file: the authorities and the states each add up to the country's 56,121 MW operating, and planned MW likewise; a place's planned years add up to its planned MW and its years of start to its operating MW.

**What answers to the hand.** Both lists, the Show button, the chart under mouse and finger, the Chart and Table switch, an authority's and a state's name as a link, a fresh link, an address naming no place (opens on ERCOT). The keyboard walks 105 stops with a focus mark each. The back button: row S1 (the table goes back to CAISO, the list keeps AZPS).

**Quiet faults.** None. 0.3 s to load.

Pictures: `docs/reviews/browser-read-2026-11-20/storage-places/as-it-opens-1280.png` (ERCOT beside CAISO); `texas-beside-arizona-public-service-1280.png` (after the choice of a state and an authority).

## 14. `/states`: a page for every state

The data machine's page (chain 581). Read with `runs/c620/b_states.mjs`: all 52 places opened one after another.

**Five cases.**
1. *A state energy office in Georgia.* What does Georgia run on, beside West Virginia? Chooses both: the last twelve months by source, the mix by year, two charts each. Answered.
2. *A retail supplier.* What do Texas's homes pay against its industry? "What its homes, businesses and industry buy and pay": sold, paid, average price and customers by sector. Answered.
3. *An AI lab's siting analyst.* Who operates the grid in a state, and does it have a large-load law? "Who operates its grid" by share of the people; then the last section. For Texas the page says no law is held (row 1).
4. *A developer.* What is built and what is coming? Capacity by source, the largest plants with county, operator and authority, what is planned by year. Answered.
5. *A student.* Alaska beside Hawaii, the District of Columbia alone: each opens whole at 390 px, no blank chart. Answered.

**Figures.** Over the 52 places, 3,601 figures at 1280 px agree with `site/data/states/<st>.json`: the last twelve months' generation by source and each share, what each sector bought, paid, its price and customers, capacity by source (nameplate and net summer), the ten largest plants, each authority's share of the people. Inside each file: the sources add up to the total, each share is its source over the total, each price is revenue over sales. At 390 px: 409 of 409 over four choices. Not set beside the file tonight: the mix by year, the planned capacity by year, gas, total energy and what moves across the border (their figures are sums over months or picks of a year).

**What answers to the hand.** The five lists; nine Chart and Table switches; every chart under mouse and finger; an address naming no state opens on Texas. The keyboard walks 41 stops. No state takes more than 0.6 s to load. The back button: row S1.

**Quiet faults.** None over the 52 places: no "undefined", no empty chart, no sideways scroll, no error.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | The page as it opens (Texas), its last section | "Not held for this place: the ERW's large-load research holds no state law for Texas." The policy monitor's own files speak of Texas's SB 6 | A reader takes it as "Texas has no law". 25 of the 52 files hold a law; the other 27 read the same way | filed (data request 563) |

Pictures: `docs/reviews/browser-read-2026-11-20/states/as-it-opens-1280.png` (Texas); `georgia-beside-west-virginia-1280.png` (two states side by side).

## 15. `/industry`: energy by industry

The data machine's page (chain 505). Read with `runs/c620/b_industry.mjs`.

**Five cases.**
1. *A gas supplier.* How much did industry use last month and against a year before? The monthly table: July 2026, 2,714 TBtu in all, each source with its change on the year. Answered.
2. *A chemicals analyst.* Which fuels does the chemical industry burn, in the South? Chooses the region; the table of industries by fuel redraws; a withheld cell says EIA withholds it. Answered.
3. *A state planner in Arkansas.* Arkansas's industrial petroleum use in 2019 beside Louisiana's, with price and spending. Chooses the state, the source and the year. Answered.
4. *An AI lab's analyst.* What does EIA project for an industry under high electricity demand? The outlook: an industry, a series, two cases side by side to 2050. Answered.
5. *A student.* How has industry's energy moved since 1973? Chooses "from 1973"; the chart under the mouse gives each month's figures. Answered.

**Figures.** Four families set beside `site/data/industry.json` as numbers at the screen's own decimals: the month and the month a year before with the change, each industry's fuels in the region chosen, each state's use, price and spending in the year chosen, the outlook by case and year. 453 figures a view; over the page as it opens and eight choices, 4,530 agree and none differs. At 390 px: 457 of 457.

**What answers to the hand.** The twelve lists, four charts under mouse and finger, four Chart and Table switches, the same address opened fresh. The keyboard walks 36 stops. The back button: row S1.

**Quiet faults.** None. 0.7 s to load.

Pictures: `docs/reviews/browser-read-2026-11-20/industry/as-it-opens-1280.png`; `after-choices-1280.png` (the Northeast, petroleum, 2019, bulk chemicals, from 1973).

## 16. `/ai-energy`: energy per AI query, as published

The data machine's page (chain 505). Read with `runs/c620/b_ai_energy.mjs`.

**Five cases.**
1. *An AI lab's energy lead.* What has Google printed for one prompt? "0.24 Wh", the median Gemini Apps text prompt, with the sentence it comes from and its page. Answered.
2. *A journalist.* Which figures are peer-reviewed? Each row names its publisher's kind; the headline says 2 of the 9 publications are peer-reviewed papers. Answered.
3. *A utility forecaster.* A fleet's electricity in a year: chooses the measure; only those rows stay. Answered.
4. *A student.* The oldest figure first: the order "Date, oldest first". Answered.
5. *A sceptic.* Is the number really in the publication? Each row quotes the words, with the page, and links the publication; the hover gives the day it was saved and its checksum. Answered.

**Figures.** 23 of 23 figures as the file gives them, at both widths; the counts (23 figures, 9 publications) and the newest (9 July 2026, Microsoft). Each figure's digits are in its own quoted words but one, which the paper prints as "1.0x10-4 kWh" and the page as 0.0001 kWh: the same number. Each row's link is the file's address.

**What answers to the hand.** The four orders are those orders, each with every row; each of the thirteen measures shows only its own rows. The keyboard walks 29 stops. At 390 px the table (1,100 px) scrolls inside its own frame. The back button: row S1.

**Quiet faults.** None. 0.2 s to load.

Pictures: `docs/reviews/browser-read-2026-11-20/ai-energy/as-it-opens-1280.png`; `one-measure-1280.png` (one measure chosen).

## 10 and 25. `/map`, Projects: the lines on the map, and a project's proposed date

The data machine's layers (chain 581) and dates (chain 505). Read with `runs/c620/b_map_lines.mjs` and `runs/c620/b_map_finger.mjs`.

**Five cases.**
1. *A transmission planner.* Which lines of 230 kV and above cross a region, and whose are they? Switches the lines on: 10,692 lines are drawn over the projects; the mouse on one gives its two ends, its owner, its voltage and its length as HIFLD draws it ("CAPTAIN JACK to SYCAN, BONNEVILLE POWER ADMINISTRATION, 500 kV, 96.5 km"). Answered, where HIFLD names the ends (row 1).
2. *A gas liquids analyst.* Where do the HGL pipelines run and how long is one? The second switch: 133 lines; "Elk Creek Pipeline, ONEOK, 1362.41 km (EIA gives no capacity)". Answered; the page says EIA gives no capacity.
3. *A developer.* When is a planned plant meant to start? The mouse on a planned unit: "Portage Solar, LLC: Solar, 250.0 MW, under construction, half or less complete, WI, MISO, 2027-07 (planned operation)". Answered.
4. *A siting analyst on a phone.* A finger on a unit at 390 px brings up its tip and opens its card under the map; a finger on a line brings up the line's tip. Answered.
5. *A student.* What is not drawn? The "i" beside "Lines on the map" says which of EIA's layers are not served and why. Answered.

**Figures.** Each line's tip beside its layer file (`site/data/map_layers/`): the three transmission tips read and the three pipeline tips read are rows of the files (voltage, length, owner; Elk Creek 1362.41 km and Lakehead 1510.45 km). The files hold 10,692 lines (299,994 km) and 133 lines (57,715 km).

**What answers to the hand.** Both switches are off as the page opens; each is read and changes the drawing when pressed, and the map shows no line once it is off again; by mouse and by a finger. A line layer is kept in the page, not in the address. With a line's tip showing at 390 px the page measures 489 px wide, and does not move sideways (the tip's own box before the chart places it): nothing a reader sees.

**Quiet faults.** None at open; 2.1 s to load at 1280 px, 1.2 s at 390 px.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | The transmission lines on, a finger on a line | "UNKNOWN201257 to UNKNOWN203126, HIGH PLAINS POWER INC, 230 kV". "UNKNOWN<number>" is HIFLD's own mark for an end it does not name: 881 of the 10,692 lines have both ends so marked and 2,861 one | An end HIFLD does not name said to be unnamed, its mark kept | fixed on `wip/9601-line-ends-unnamed` |

Pictures: `docs/reviews/browser-read-2026-11-20/map-lines/as-it-opens-1280.png`; `transmission-on-1280.png` (the lines of 230 kV and above); `hgl-on-1280.png` (the HGL pipelines).

## 12, 13 and 21. The Grid tool's map: the Price color and each authority's own facts

The map is the portable laptop's (chain 504); the Price color and the panel's "Its own facts" are the data machine's (chain 505). Read with `runs/c620/b_grid_map.mjs` and `runs/c620/b_grid_demand.mjs` at `/grid?grid=us48&view=network&shape=map`.

**Five cases.**
1. *A power trader.* Where was day-ahead power dearest yesterday? Presses Price: three areas are colored, green 31.93 (SPP North) to red 54.09 USD/MWh (ERCOT's hub average), each the day 16 November; PJM, New York, New England read "license needed" and MISO "not shown (MISO's terms are under review)". Answered for the three grids whose prices are public; the page says why the rest are blank.
2. *A battery developer.* Where are hours below zero most common over twelve months? The measure "Hours below zero, twelve months"; the legend gives both ends. Answered.
3. *A student of one grid.* What does TVA own, and whom does it lean on? Presses TVA: 44,697 MW in 468 generators (gas 18,592, nuclear 8,835, coal 7,644, hydro 4,888), record demand 35,086 MW, MISO its first partner. Answered. Its carbon intensity reads "not held", with why (EIA's estimates cover the seven ISOs and the Lower 48 only).
4. *An AI lab's siting analyst.* How fast has demand grown in Arizona Public Service's area, and what large loads are spoken of there? The panel: demand in 2025 up 31 percent on 2019, 2 public rows of large loads. Answered.
5. *A transmission planner.* How much does ERCOT take in right now, and against what demand? The hover gives net imports (203 MW over 2 ties); demand reads "not held for this hour" (row 1).

**Figures.** The Price color: for each of the eight measures the legend's two ends and the hover of eight authorities (three shown, four held or paused, one with no public price) agree with `site/data/regions/prices_map.json`. "Its own facts" for TVA, ERCOT, Arizona Public Service, CAISO and Seminole Electric: what each owns, its generators, its carbon intensity, its record demand, its first partner and its large-load rows agree with `site/data/regions/authority/<code>.json`; shares and growth are printed to two figures (40.6 reads "41%").

**What answers to the hand.** The color that opens is carbon intensity (the standing ruling); Price is a switch beside it, by mouse and by a finger; a finger on ERCOT at 390 px shows its card and opens its panel; the page is 390 px wide. The regions are drawn 2.5 s after the address is opened at 1280 px and 2.0 s at 390 px. The seven decisions behind the price colors each give Default and Source on hover. The price color is kept in the page, not in the address: a link opens the carbon color, as the ruling has it.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | The mouse on any authority at the hour the map opens on, then the slider stepped back | "Demand: not held for this hour" from 2026-11-18 04:00 back to 2026-11-16 00:00 UTC, for every authority; ERCOT's last figure is 52,838 MW at 2026-11-15 22:00. The line under the map says "Demand of the seven ISOs: newest hour 2026-11-20 08:00 UTC". The live set's demand ends on 15 November 23:00 UTC (read at 11:18 UTC on 20 November) | Demand for the hour shown | filed (data request 565). Read again at 16:31 UTC: the live set now holds demand to 19 November 23:00 UTC and carbon intensity to 17 November; `/grid?grid=ercot` heads its demand "Nov 19, 5:00 PM CST" and the network's panel for ERCOT at the opening hour reads "203 MW, 0.41 percent of its 49,812 MW demand". The map's hover still reads "not held for this hour" for the same hours: its hourly file was last refreshed at 12:05 UTC, before the load |
| 2 | A press on Seminole Electric (SEC) | "Net imports met -592 percent of its demand." 26 of the 58 authorities' files hold a share below zero | A sentence about what it sent out | fixed on `wip/9601-authority-facts-words` |
| 3 | TVA under the mouse, any hour | "Demand: not held for this hour": the map never holds demand for an authority outside the seven ISOs, at any hour | "for this hour" suggests another hour would hold it. The map's own words (chain 504) | ruling |

Pictures: `docs/reviews/browser-read-2026-11-20/grid-map/as-it-opens-1280.png` (the map as it opens, carbon color); `price-color-twelve-months-1280.png` (the Price color, the average over twelve months); `tva-its-own-facts-1280.png` (TVA's panel).

## 17. `/demand?view=country#forecast`: the forecast beside what happened

The data machine's section (chain 505). Read with `runs/c620/b_forecast.mjs`.

**Five cases.**
1. *A utility forecaster.* How far off is the day-ahead forecast for Tennessee? As the page opens (Tennessee and the Carolinas): hours with both, the mean miss and the bias, overall, by season and by hour of the day. Answered.
2. *A trader.* On which days did Texas's forecast miss the peak most? "The hottest and coldest days": each day's temperature, peak forecast, peak demand and miss. Answered.
3. *An event analyst.* How did the forecast do in each of the nine events? The table of events: hours, miss, bias, peak miss; an event with no hour held is blank. Answered.
4. *A renewables analyst.* ERCOT's and CAISO's wind and solar forecasts against output. Answered for those two; not set beside the file tonight (20 figures a view, from `renewables_forecast.json`).
5. *A student.* An authority beside its region (New England beside PJM, the Northwest beside BPA). Answered; a place that files no forecast reads "not held" with why.

**Figures.** Every marked figure of the section for seven pairs of places (thirteen places), as numbers at the screen's decimals, beside `site/data/regions/forecast/<place>.json`: 1,456 of 1,456 at 1280 px, 209 of 209 at 390 px.

**What answers to the hand.** Four Chart and Table switches give a table; the line charts answer the mouse with a card; the bar charts of the view give their figures as the browser's tooltip (row S2). 390 px wide at 390. 1.7 s to load.

Pictures: `docs/reviews/browser-read-2026-11-20/demand-forecast/as-it-opens-1280.png` (Tennessee and the Carolinas); `texas-beside-california-1280.png`.

## 18. `/demand?view=country`: the whole country, any two places (read in full by the desktop's second window)

The old laptop's page (chain 503), read in full on production on 20 November between 19:55 and 20:25 UTC by the desktop's second window (session 9203), which took the chain over. Scripts: `runs/c620w2/dump.mjs` (every table, every Chart and Table switch pressed), `runs/c620w2/cmp_demand.py` (recomputes from `site/data/regions/demand/<place>.json` without the page's code), `runs/c620w2/hand.mjs`. The old laptop's last fixes to this page (session 8480: the 95 percent rule on a blank weather cell's hover, a day whole only on all the hours of its local day, the authorities across the border) are still not on main; what is read here is production as it is.

**Five cases.**
1. *A TVA planner.* How has Tennessee's demand moved since 2019, and when was the record? As the page opens (Tennessee beside the Carolinas), "Year by year": 18,190 MW on average in 2019, 19,490 in 2025 (+7.15 percent), 20,098 in 2026 to October (+9.48 percent on 2019's same ten months); the record hour 35,086 MW on 22 January 2025 at 07:00. Answered.
2. *A Texas analyst.* Is ERCOT the whole of the Texas region? Chooses ERCOT beside Texas: two places side by side, each with its own year rows and its own highest hour. Answered, the page names what each sums ("balancing authorities summed").
3. *A Northwest utility.* BPA's growth against its region's: BPA +9.41 percent from 2019 to 2025 and +15.11 percent for 2026 to October; the Northwest +6.91 percent, with no row for 2020 (its file holds no 2020) and "not held" for 2021's change on the year before. Answered, the gap said.
4. *A datacenter siting analyst.* When in the year and day has demand grown most? "Where the growth is": Tennessee's largest cell January at 02:00, +24.81 percent (4,477 MW); the Carolinas' January at 03:00, +28.64 percent (6,942 MW). Answered: winter nights, not summer afternoons.
5. *A student.* Yesterday's demand: "The newest days", seven days of each place (Tennessee 458.3 GWh on 16 November, highest hour 22,058 MW). Answered.

**Figures.** As it opens and after two choices (ERCOT beside Texas; the Northwest beside BPA), every cell of "Year by year", the summary of "Demand by day", "The newest days", the first 500 rows of each place's daily table and the two sentences under each month-by-hour grid, recomputed from the files: **6,431 figures, none differs.** The 2026 row is set against 2019's same months, as its label says. Two figures that look odd are the file's own: Tennessee's forecast on 7 July 2018 equals its demand (22,987 MW both, a miss of 0); and every "With the weather taken out" row for Tennessee reads "not held" because the file holds no figure for the year's energy in any year from 2022.

**What answers to the hand.** The keyboard alone at 1280 px: 62 stops from the top to the foot, each in sight with a focus mark. A finger at 390 px on the eight charts, four places each: a card on every chart; the page stays 390 px wide. A link that carries two places opened fresh reads them in its lists; after two choices the back button gives the first choice's address and lists that read what the page shows. No error in the page.

**Quiet faults.** None: 390 px wide at 390 (the first pass); 0.8 to 1.8 s to load at 1280 px.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | "Where the growth is", the Carolinas | August is white across the month-by-hour grid and has no bar in "by month"; the hover says "August, 12:00: not held" and "Aug: not held", not why. The file holds no hour of 1 or 2 August 2025 for the Carolinas, so 2025's August has no average | A blank with its hover, as the page has it; the hover could say which days are missing | noted |

Pictures: `docs/reviews/browser-read-2026-11-20/demand-country/as-it-opens-1280.png` (Tennessee beside the Carolinas, the page as it opens); `year-by-year-1280.png` (the year rows and the record hours); `where-the-growth-is-1280.png` (the month-by-hour grids, the Carolinas' blank August); `ercot-beside-texas-1280.png` (after the choice ERCOT beside the Texas region).

## 19. `/supply#whole-country`: net imports, who trades with whom, the mix by region (read in full by the desktop's second window)

The old laptop's section (chain 503), read on production on 20 November between 20:35 and 21:05 UTC by the desktop's second window (session 9203). Scripts: `runs/c620w2/dump.mjs`, `runs/c620w2/cmp_supply.py` (from `site/data/regions/trade/<region>.json`, `trade_matrix.json` and `mix/<region>.json`, without the page's code), `runs/c620w2/hand.mjs`. The old laptop's last fixes to this page (session 8490: a pair's mean and percent hovers, the months a year holds, a figure that rounds to zero read 0.0, a mix year with no month held) are still not on main.

**Five cases.**
1. *A TVA trader.* Whom does Tennessee lean on, month by month? Tennessee beside the Midwest: in January 2025 Tennessee took in 999.2 GWh net, 2,163.2 GWh of it from the Midwest, while sending power to the Southeast and the Carolinas. Answered.
2. *A regulator.* Do the two ends of a line agree? The year's table by neighbour: Tennessee's own report against each neighbour's, the gap over the hours both reported, its percent. Answered; the hover says why the gap need not be the two columns' difference (each column runs over its own side's hours).
3. *A California analyst.* Who sends California its power? "Who trades with whom, 2025": the Northwest sent 14,800.6 GWh by its own report (14,598.6 by California's), the Southwest 24,249.7 (25,970.3), a gap of 8.3 percent, marked large. Answered.
4. *A balancing authority's planner.* Its partners in order: 62 authorities, by gross and by net exchange (AECI: MISO, SWPP, SPA, TVA, SIKE by gross). Answered.
5. *A student.* What does Tennessee run on? The mix by month: January 2025, gas 39.6, nuclear 30.9, coal 18.8, hydro 9.6 percent of 16,294.6 GWh, 31 days of 31 held; storage "not held yet". Answered.

**Figures.** As it opens and with two pairs chosen (Tennessee beside the Midwest; the Northwest beside California): every month of each region's net imports, in all and by neighbour; the year's table by neighbour (own report, the neighbour's, the gap and its percent, months held); the months of 2025; all 25 pairs of regions and 157 pairs of authorities (each side's report, the mean, the gap); the partners of 62 authorities; each month's share by source and the months of 2025 with net generation and days held. **11,119 figures, none differs from its file.** One row the comparer could not place, "PNM and SWPP, no net flow", is the file's own pair with a direction of "none" and both reports 0 for 2025.

**What answers to the hand.** The keyboard alone at 1280 px: 236 stops from the top to the foot, each in sight with a focus mark. A finger at 390 px on the 14 charts, four places each: a card on every one; the page stays 390 px wide. A link carrying two regions opened fresh reads them in its lists; the back button after two choices gives the first choice with lists true. No error.

**Quiet faults.** None. 1.0 to 2.7 s to load at 1280 px (2.7 s the first time, a page not yet in the server's cache).

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | "Who trades with whom, 2025", the pair PNM and SWPP | Both reports 0.0; the gap's percent reads "not held yet" | A percent of two reports that are both zero can never be held; "not held" with its hover (which says a percent needs two reports not both zero) would not promise a later figure. A choice of words | ruling |

Pictures: `docs/reviews/browser-read-2026-11-20/supply-country/as-it-opens-1280.png` (the page as it opens); `the-whole-country-1280.png` (the section, Tennessee and its neighbours); `who-trades-with-whom-1280.png` (the pairs of regions for 2025); `tennessee-beside-midwest-1280.png` (after choosing Tennessee beside the Midwest).

## 20. `/events` and `/events/<event>#whole-country`: the thirteen regions across each event (read in full by the desktop's second window)

The old laptop's section (chain 503), read on production on 20 November between 21:05 and 21:40 UTC by the desktop's second window (session 9203). Scripts: `runs/c620w2/dump.mjs`, `runs/c620w2/cmp_events.py` (from `site/data/regions/events/<event>.json`, without the page's code; `RULE=page` follows the page's own counting, `RULE=both` the section's stated rule), `runs/c620w2/hand.mjs`. Four events were read in full: Elliott as it opens, Uri with Texas beside Central, the June 2025 heat with the Mid-Atlantic beside New York, COVID-19 with California beside the Northwest. The old laptop's last fixes to this section (session 8470, eleven commits: among them the hours a region's percent rests on, said on hover) are still not on main.

**Five cases.**
1. *A grid operator in the Carolinas.* How far above normal did Elliott push demand? "Each region across the event": the Carolinas 8,542.5 GWh over the window, +29.3 percent on the baseline, the highest hour 44,630 MW at 2022-12-24 11:00 UTC against 26,915 MW in the baseline that hour. Answered.
2. *A Tennessee planner.* Who sent Tennessee power during Elliott? "Power between regions, pair by pair": the Midwest to Tennessee, 3,407 MW on average and 909.7 GWh over the window, against 1,220 MW in the baseline. Answered.
3. *A Texas analyst.* Did Texas import during Uri? Texas beside Central: each region's demand, net imports and generation by source over the window, the event against its baseline. Answered.
4. *A California utility.* What did COVID-19 do to California and the Northwest? California beside the Northwest over 2,210 hours: demand against the baseline, the two regions' charts one beside the other. Answered.
5. *A student.* Which regions did a storm reach? The sentence over the table counts the regions whose demand stood 5 percent or more from the baseline, with the list on hover. Answered.

**Figures.** Every figure of "Each region across the event" (13 regions) and of "Power between regions, pair by pair" (25 pairs) for the four events: **912 figures, all agree with the file as the page counts them.** Set beside the rule the section itself states, 12 differ (row 1).

**What answers to the hand.** The keyboard alone at 1280 px: 101 stops from the top to the foot, each in sight with a focus mark. A finger at 390 px on 15 charts, four places each: a card on every one; 390 px wide throughout. A link carrying two regions opened fresh reads them; the back button after two choices gives the first choice with lists true. No error.

**Quiet faults.** None. 1.8 to 2.9 s to load at 1280 px.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | "Power between regions, pair by pair", set beside "How a figure here is formed" ("Each figure is a sum or a mean over the hours of the window that the file holds for both the event and the baseline") | A pair's mean and sum run over the hours its flow is held, and its baseline mean over the baseline's own hours (`pairs()` in `site/lib/countryfiles.ts`). Elliott, Central and Canada: 17 MW over 267 hours against a baseline over 219; over the hours both hold the mean is 10 MW and the sum 2.2 GWh, not 4.5. COVID-19, the Midwest to Central: 3,892 MW over 2,209 hours, 3,897 over the 2,207 both hold. 10 of the 224 pairs drawn over the nine events rest on different hours | The table and its note agree, and a pair's event and baseline means rest on the same hours, as the regions' figures do. Which way (the note's words, or the pair's hours) is a choice of method on the old laptop's page, whose pending branch `wip/8440-events-regions-done` changes the same lines and keeps this rule | ruling |
| 2 | "Each region across the event", COVID-19, Florida | "Hours held 2,187 of 2,210" beside a demand summed over the 1,790 hours the event and the baseline both hold. The column says what it counts ("the hours ... for which the file holds the region's demand"), and the demand's hover says it is over the hours both hold | A reader takes the figure to rest on 2,187 hours. The old laptop's session 8470 (not on main) names the hours a region's percent rests on in the hover | noted |

Pictures: `docs/reviews/browser-read-2026-11-20/events-country/events-index-1280.png` (the list of events); `elliott-as-it-opens-1280.png` (Elliott's page as it opens); `elliott-the-whole-country-1280.png` (the section, Tennessee and the Carolinas); `elliott-each-region-1280.png` (the thirteen regions across the storm); `elliott-pairs-1280.png` (the pairs of regions); `uri-texas-beside-central-1280.png` (Uri, after choosing Texas beside Central).

## 1, 2, 5 and 22 to 26: the pictures still wanting, and what was seen taking them (the desktop's second window)

Taken on production on 20 November about 21:40 UTC (`runs/c620w2/pics.mjs`). Items 22 to 24 were read in full by chain 504 (`docs/reviews/grid-map-read-2026-11-19.md`) and opened again for quiet faults by the portable laptop (item 4 above); their figures were not read again here.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | `/grid?region=ten`, the Mix tab, "The latest hour held" | "2026-11-17 05:00 UTC (Mon, Nov 16, 23:00 in Tennessee)", while the Lower 48 on the same tool reads 2026-11-19 23:00 UTC. The region page files were built on 19 November and not since; each page says the hour it holds | The same day of data across the tool, or the file's day said beside it | filed (data request 570) |
| 2 | The same table | "Solar -5 MW, -0.0%": EIA's figure (solar plants draw power at night), its share printed as "-0.0%" | A share that rounds to zero; the sign says it was below zero. The old laptop's session 8490 reads such a figure "0.0" on `/supply`; the two pages would then differ in how they print it | noted |
| 3 | The 3D network as it opens, its legend | "Carbon intensity ... latest hour 2026-11-17 23:00 UTC"; the network's week opens on 2026-11-19 04:00 UTC. The color is two days behind the links | Part of the live set's lag (data requests 565 and 569) | noted |

Pictures, under `docs/reviews/browser-read-2026-11-20/more/`: `findings-as-it-opens-1280.png` (item 1, the sheet of forty first); `problem-sets-index-1280.png`, `set-storm-across-the-country-1280.png`, `set-your-own-balancing-authority-1280.png` (items 2 and 11); `resource-map-as-it-opens-1280.png` (items 5 and 23, the map itself); `region-tennessee-mix-1280.png` (item 22, the latest hour held, the solar share of -0.0%); `region-tennessee-network-map-1280.png` (item 21 and 22, the map of the authorities with Tennessee chosen); `region-southwest-clean-1280.png` (item 22, the Clean tab); `network-3d-as-it-opens-1280.png` (item 24, the 3D network and its legend); `method-ba-boundaries-1280.png` (item 26).

## Part C: the same number in two places

Each pair read on production on 20 November between 11:40 and 11:50 UTC (`runs/c620/survey.mjs` into `runs/c620/c1/`, and the page files).

| # | The pair | One place | The other | Verdict | State |
|---:|---|---|---|---|---|
| C1 | The batteries of `/storage/places` against `/storage` | `/storage/places`, the seven grids: ERCOT 19,195 MW operating and 24,159 planned; CAISO 17,266 and 10,878; PJM 666 and 825; MISO 1,176 and 3,938; NYISO 269 and 829; ISO-NE 1,022 and 1,051; SPP 491 and 1,685 | `/storage`, "By ISO": ERCOT 19,194.60 operating, 7,899.50 under construction and 16,259.30 planned (24,158.8 together); CAISO 17,265.50, 4,733.70 and 6,144.10 (10,877.8); PJM 665.90 and 825.1; MISO 1,175.90 and 3,938.2; NYISO 268.70 and 828.5; ISO-NE 1,021.70 and 1,050.5; SPP 490.50 and 1,684.5 | The same, to the megawatt. `/storage` splits planned from under construction and prints two decimals; `/storage/places` adds them and prints none | agrees |
| C2 | An authority's own facts in the map's panel against `/demand?view=country` | The panel, TVA: record demand 35,086 MW, 2025-01-22 07:00 local; demand in 2025 up 7.2 percent on 2019 | `/demand?view=country&a=ba-tva`: highest hour 35,086 MW, 22 January 2025, 07:00; average demand +7.15 percent from 2019 to 2025 | The same; the panel prints two figures | agrees |
| C3 | The same panel against `/supply` | The panel, TVA, 2025: MISO 17,649,857 MWh in, net | `/supply?region=ten`, "Who trades with whom, 2025": Midwest to Tennessee, 15,679.2 GWh by the sender, 16,681.5 GWh by the receiver | Not the same thing, and each says what it is: the panel is one authority with one authority; the page is EIA's Midwest region (MISO and its neighbours) with the Tennessee region. A reader who takes "Midwest" for "MISO" finds 17,650 against 16,682 GWh | noted |
| C4 | A storm's megawatts on an event page against the region's demand that day | `/events/elliott-2022`, Tennessee: highest hour 33,225 MW at 2022-12-24 01:00 UTC | `/demand?view=country&a=ba-tva&days=2022`: the year's highest hour 33,225 MW, 23 December 2022, 19:00 (local) | The same hour and figure, one in UTC and one in local time, each labelled | agrees |
| C5 | The map's Price color against `/prices/compare`, the average over twelve months | The map: ERCOT's hub average 34.86, CAISO SP15 30.29, SPP North 34.50 USD/MWh | `/prices/compare`, "the twelve months to October 2026": 34.59, 30.27 and 34.27 | Both right, on different windows: the map's is the 365 days to its file's day (16 November), the comparison's the twelve calendar months to October. The map did not say which days | fixed on `wip/9601-price-map-window` (the hover names the window's days) |
| C6 | The board's price against `/prices` | `/board`: ERCOT hub average, day-ahead, 54.09 USD/MWh, "16 Nov 2026 (stale)"; real time 22.68, 18 November | `/prices`: HB_HUBAVG 21.29 at 2026-11-20 11:00 (a 15-minute price); day-ahead "no data: no iso_dam_hub_prices row since 2026-11-19 11:00 UTC" | Not the same measure (a day's mean against the newest interval), and both behind: the board's newest whole day-ahead day is four days old, the price page's day-ahead hours stop a day ago. Part of the lag of data request 565; the map's 30-day figure for ERCOT is blank for the same cause ("673 of the window's 721 hours held") | filed (565) |
| C7 | A state's mix on `/states` against its region's on the Grid tool | `/states?a=TX`, the last twelve months (EIA's state generation): gas 47.3%, wind 22.3%, solar 12.6%, coal 10.7%, nuclear 6.5% | The Grid tool: ERCOT's own facts over 2025-11 to 2026-10 (EIA-930): gas 40%, wind 24%, solar 16%, coal 12%; the Texas region, October 2026: gas 45.0%, wind 20.9%, solar 15.1% | Not the same thing: the state holds plants outside ERCOT and plants that report to EIA and not to the grid operator; the periods differ. Each page names its source. A reader comparing "Texas" with "Texas" sees gas at 47 against 40 percent | noted |
| C8 | "The last twelve months" on the two sibling tools of ERCOT (read by the desktop's second window, 22:50 UTC) | `/cost-of-power/seller`, solar at the hub average: "Over the last twelve months, Oct 2025 to Sep 2026 ... the flat average of USD 32.17" | `/cost-of-power`, a flat load at LZ_NORTH: "USD 34.07 per MWh over the last twelve months ... Nov 2025 to Oct 2026" | Two windows of the same name a month apart (the generator tool's window ends where its generation profile ends), and two places. Each names its months. A reader who sets the two side by side compares September with October | noted |
| C9 | The latest hour of the Grid tool's thirteen regions against its Lower 48 (the desktop's second window, 21:45 UTC) | `/grid?region=ten`, Mix: "The latest hour held 2026-11-17 05:00 UTC" | `/grid`, the Lower 48: the hour starting 2026-11-19 23:00 UTC | The region page files are of 19 November; each page says the hour it holds | filed (data request 570) |

## Part D: the first minute

Read with `runs/c620/d_first_minute.mjs`, `d_menu_phone.mjs`, `d_ways_in.mjs`, `d_headings.mjs` and the tour's own check, at 1280 and 390 px.

**As a stranger (no cookie).** Every address answers the in-review page ("This tool is in review and will open when it is approved. Open now. Home"), 390 px wide at 390, in 0.2 to 0.5 s; `/internal/findings` answers "No page at this address". Nothing of a page in review reaches a stranger.

**As a reviewer (the internal view).** The home page opens in 0.3 s. The menu has six groups and 33 entries; with the home page's links, the foot's and the tour's, 53 addresses were asked for: 52 answer with their own heading, one does not (row D1). `/ask` goes to the Grid tool with its Ask panel open, as session 299 made it. Each group opens on a press and on a finger's tap; its list stands inside the screen at both widths; each entry opens its page; a second press closes the group. The keyboard reaches "Skip to content", the wordmark, the six groups and the four links in that order, each with a focus mark.

**The tour.** Fifteen stops; each has its bar, Back and Next and opens its page. Seven of the headings the stops quote were not among their pages' headings on production (rows D2 to D6).

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| D1 | The menu, Analysis, "Policy" | A page that is the two words "license needed" and nothing else: no heading, no views, no link (the hover: one publisher's permission is not recorded). `/policy?view=week` and the monitor draw, and cannot be reached from it | The page's heading and its views, with the reason where the list would be | fixed on `wip/9601-policy-held-page` (nothing held is drawn) |
| D2 | Stop 1, `/cost-of-power/battery`: "Change the battery's hours under "Your battery"" | No "Your battery" on the page: the box is "Assumptions" since the ruling of 15 October (session 296) | The stop names the box as the page does | fixed on `wip/9601-tour-headings` |
| D3 | Stop 4, `/grid`: "One grid at a time, ERCOT first ... read "Right now: demand"" | `/grid` opens on the Lower 48 (since session 299); "Right now: demand" and "Who runs this grid" are on ERCOT's page | The stop opens the page its words describe | fixed on `wip/9601-tour-headings` (the stop opens `/grid?grid=ercot`; see "Decisions made without you") |
| D4 | Stop 7, `/digest`: "Read "Top of the industry", then "ERW's Numbers Today"" | "No Digest yet for Friday 20 November 2026 ... The newest is the Digest of Thursday 12 November 2026", and the archive. No Digest has been written since 12 November | A Digest, or a stop that opens the newest one | ruling (the Digest is paused and out of bounds here) |
| D5 | Stop 11, `/supply`: "Who trades with whom" | The heading reads "Who trades with whom, 2025" | The words are on the page; the tour's check wanted the heading whole | fixed on `wip/9601-tour-headings` (the check reads a heading without its year) |
| D6 | Stop 12, `/map?tab=resources`: "then "How the map is drawn"" | The heading is inside the fold "Method note", closed until a reader opens it | The stop says to open the fold | fixed on `wip/9601-tour-headings` |
| D7 | The ways in to the week's pages: the links of 18 pages read (the home page, the menu, `/queues`, `/storage`, `/curtailment`, `/demand`, `/supply`, `/grid`, `/map` and others) | `/states`, `/industry` and `/ai-energy` are reached only from the tour (stops 13 to 15). `/queues/places`, `/storage/places` and `/curtailment/where-when` are linked from no page: a reader needs the address | A way in from the menu or from the page each belongs under. Where each goes is the menu's question | ruling |
| D8 | A stranger at the home address | The in-review page's heading is "/" (and "/states", "/industry" for the pages with no name in the release list) | A name. The list of names is `site/lib/release.ts`, not touched here | ruling |
| D9 | The menu at 390 px, one group open | The open list covers the names of the groups on the rows under it (Economics open: Infrastructure, Analysis, Games and About are under it) | A reader closes the first group (a second press) to reach the next. The menu's own behaviour, older than this week | noted |

Pictures: `docs/reviews/browser-read-2026-11-20/first-minute/a-stranger-at-the-home-page-1280.png`; `the-home-page-internal-view-1280.png`; `the-menu-open-390.png` (the last group open under a finger).

## Part E: the pages built before 17 November, at 390 px with a finger

A first pass, the five tools Samuel calls sellable first (`runs/c620/e_phone.mjs`, 12:32 to 12:54 UTC). For each page at 390 px: the time to load; sideways scroll, "undefined", "NaN", "null", an empty chart, an error; every "i" mark that is on the screen tapped (its box inside the screen); every switch tapped; every list changed; every chart tapped at four places; after each step the page's width and its errors. The figures in the page's text at 390 px were set beside the same page at 1280 px.

| Page | Load | "i" marks on the screen | Switches | Lists | Charts under a finger | Width after every step |
|---|---:|---|---|---|---|---|
| `/cost-of-power/battery` (what a battery earns) | 0.3 s | 6 of 6 open inside the screen (3 more are in closed folds) | 30 tapped, no error | 7 changed, each changes the page | a card at 4 of 4 places | 390 px |
| `/cost-of-power/seller` (what a generator earns) | 0.4 s | 2 of 2 | 15 tapped | 6 changed | 2 charts, 4 of 4 each | 390 px |
| `/cost-of-power` (what a datacenter pays) | 2.4 s | none drawn as marks | 17 tapped | 5 changed | 4 of 4 | 390 px |
| `/research` (Automated Analysis) | 0.2 s | none | 30 of 221 tapped | 6 changed | 10 charts, 4 of 4 each | 390 px |
| `/grid` (the Grid tool, the Lower 48) | 1.1 s | none | 6 tapped | 2 changed | 3 charts, 4 of 4 each | 390 px |

- **Then 22 more pages of the menu, the same pass:** `/board`, `/prices`, `/prices/compare`, `/supply`, `/contracts`, `/severance`, `/impact`, `/battery/customer`, `/shoulder`, `/demand`, `/curtailment`, `/storage`, `/datacenters`, `/deals`, `/companies`, `/deals/capital`, `/events`, `/thesis`, `/play/battery`, `/learn/bill`, `/data`, `/about`. On none does the page scroll sideways at any step, show "undefined", draw an empty chart or raise an error; every "i" mark on the screen opens its box under a finger from a fresh page (checked one by one on `/impact`, 29 marks, and `/cost-of-power/battery`).
- **The figures at 390 px are the figures at 1280 px** on `/cost-of-power/seller` (501 figures in the text) and `/cost-of-power` (497), in the same order. On the battery page, `/research` and `/grid` the text differs only by a chart's own axis labels, which a narrower chart draws fewer of.
- **The keyboard alone at 1280 px on the five tools** (`runs/c620/e_keys.mjs`): the Tab key walks 70, 78, 72, 361 and 66 stops in the page and reaches the foot; every stop is seen and carries a focus mark; Enter presses a switch. On the battery and the generator tools a choice rewrites the address in place, so the browser's back button leaves the tool rather than undoing the choice: the tools' own behaviour since they were built (the address always holds the choices), noted.
- **The standing rulings on the Grid tool, as seen on production:** the color that opens is carbon intensity; the 3D network opens first; the "Watch" stories (Live now, California's evening, Texas during Uri, The June 2025 heat), the Batteries switch and the side panel on a press are there at 1280 and 390 px.
- **A reader's sum on the battery page at 390 px** (`runs/c620/e_battery_sums.py`): ERCOT, 4 hours: "the last three full years, averaged: 255.08" is the mean of 2023 to 2025 as listed (530.14, 147.67, 87.44), and "the last seven full years: 739.80" the mean of 2019 to 2025; CAISO, 2 hours, holds two full years and offers neither average.
- **Figures at 390 px against the page files, for the older pages that draw from one** (`runs/c620/figures_older.ps1`, a screen: a figure is found when a number of the file rounds to it at the decimals shown): `/prices/compare` 144 found, `/board` 98, `/demand` 111, `/demand?view=country` 404, `/supply` with two regions 1,029, Elliott's page with two regions 317. The figures not found were read one by one: years written with a comma after them, figures of another table on the same page (the futures positions on `/supply`, the hub price on the event page) and the pages' own sums. None is a wrong figure.
- **Not done in this pass:** the five cases for each of these pages and their figures against the tables. The five tools' figures were replicated for their done line on 14 November (`docs/reviews/five-tools-signature-pack-2026-11-14.md`) and are not replicated again here.
- **Found in part D and belonging here:** the menu's Policy page (row D1) and six method pages at 390 px (item 4, row 1), both mended on branches.

Pictures at 390 px: `docs/reviews/browser-read-2026-11-20/phone/cost-of-power_battery-390.png`, `cost-of-power_seller-390.png`, `cost-of-power-390.png`, `research-390.png`, `grid-390.png`.

### The five sellable tools in part B's form (the desktop's second window, 22:40 to 23:00 UTC)

What the first pass above left: the figures set beside their tables, and the readers' cases. **Figures:** `site/scripts/check-values.mjs` on production, restricted to the five tools and every page under their addresses (the battery, seller and datacenter tools by grid, `/research` and its cards, `/grid` and its seven grids with their views): **4,119 of 4,122 figures match a direct query of Supabase.** The three that did not were one page, `/cost-of-power?grid=caiso`, whose carbon window read 9,399 hours where Supabase holds 9,567. The page had been cached before the live set's load of about 16:00 UTC, and the visit itself rebuilt it: read again a minute later, 78 of 78 match. At 390 px all five open 390 px wide, with no "undefined" and no empty chart (`/cost-of-power` 3.6 s, the others under 1.5 s).

**Five cases, one a tool, each answered on the page at 390 px:**
1. *A battery developer:* what did a 4-hour battery at ERCOT's hub earn? 80.34 USD per kW over the last twelve months, 255.08 averaged over the last three full years, and 3,430.56 in 2021, the year of Uri.
2. *A solar developer:* what did a merchant plant earn? USD 59.85 per kW over October 2025 to September 2026 at the hub average, with a capture rate of 72 percent (23.27 against a flat 32.17 USD/MWh).
3. *A datacenter buyer:* what does a flat 100 MW load at LZ_NORTH pay? USD 34.07 per MWh over November 2025 to October 2026, USD 29.85 million in all, USD 0.0691 per GPU-hour. How soon can it connect? ERCOT's report of 19 June 2026 gives 8,927 MW approved to energize and 3,900 MW observed running, and the page says ERCOT estimates no wait.
4. *A researcher:* can the warehouse run an analysis? "Ask for an analysis" takes a question and up to ten public tables; each card downloads its data, its Stata do-file and its Python file.
5. *A grid watcher:* what is the Lower 48 doing? 489,761 MW in the hour starting 2026-11-19 23:00 UTC, less than the 491,760 MW of a week before; natural gas the largest source.

**The keyboard alone and a finger on the 22 other pages of the menu** (`runs/c620w2/hand.mjs`, the desktop's second window, 23:00 to 23:30 UTC). At 1280 px the Tab key walks each page from the top to the foot, and every stop is in sight with a focus mark: `/board` 140 stops, `/prices` 69, `/prices/compare` 39, `/contracts` 65, `/severance` 88, `/impact` 85, `/battery/customer` 28, `/shoulder` 121, `/demand` 50, `/curtailment` 196, `/storage` 45, `/datacenters` 55, `/deals` 27, `/companies` 92, `/deals/capital` 19, `/events` 37, `/thesis` 39, `/play/battery` 31, `/learn/bill` 53, `/about` 59, `/supply` 236. `/data` has more than the walk's limit of 700 stops (a link for every table of the warehouse); all 700 carried a focus mark. A finger at 390 px on every chart: a card on `/impact` (4 of 4), `/demand` (2), `/curtailment` (9), `/storage` (3), `/datacenters` (1) and `/supply` (14). No card on three charts whose figures are only the browser's own tooltip (SVG `<title>`): `/prices/compare`'s bars (17 figures) and `/shoulder`'s two charts (98). That is row S2, left for Samuel's ruling. Nor on `/board`'s workbench before a row is pressed, which is empty by design. No page wider than 390 px after any tap.

### Every page with a fixed address, at both widths

`runs/c620/e_all_routes.mjs`: the 80 pages of `site/app/` whose address has no variable part, each opened at 390 and at 1280 px (13:40 UTC).

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| E1 | `/data/faults` at 390 px | 417 px wide: one long unbroken word in a list of terms | 390 px | fixed on `wip/9602-faults-page-phone` (`b7a9c6676`); with the style put on production's page, 390 px wide |
| E2 | `/internal/waits` | 7.2 s to load at 390 px, 5.9 s at 1280 px | Under five seconds. An internal page | noted |
| E3 | `/data/licenses`, the record of reads | "answered at https://lustat.statec.lu/undefined" in four rows | The publisher's own answer: its server sends a robots request to an address ending "undefined", and the record says so. Not a fault | noted |

The other 77 show nothing wrong at either width; `/policy` and `/internal/findings` are the two already mended on branches.

## Landed during the night: `/congestion` and `/conditions` (the data machine's chain 601, on main at 13:43 UTC)

Read on production at about 13:50 UTC, once the deploy answered. Both are in review and in no menu; the tour gained a sixteenth stop for `/conditions`, and the tour's own check passes 95 of 102 (the same seven as before; the new stop passes). Neither page's code is edited here.

### `/congestion`

Read with `runs/c620/n_congestion.mjs`.

**Five cases.**
1. *A power trader.* Which SPP constraint cost most this year? Two tables as the page opens, by hours bound and by cost, 25 rows each, each constraint with its hours, mean and highest shadow price and cost. Answered. The names are SPP's own ("TMP128_29363 (contingency 333)").
2. *A transmission planner.* When does a constraint bind? A press on its name draws its hours by month and hour of the day, and by month. Answered at 1280 px by resting the mouse on a cell; at 390 px the grid's figures are tooltips (row S2).
3. *A battery developer in California.* Where does congestion add to the price? Chooses CAISO: the hubs and zones by mean congestion part, share of the price, hours it added and took off. Answered.
4. *A datacenter's siting analyst.* Two places side by side over a year. Answered.
5. *A student.* What about the other grids? "Not drawn: ERCOT (source needed), PJM, NYISO and ISO-NE (license needed), MISO (paused)". Answered.

**Figures.** Every marked figure and every cell of the chosen constraint's grid, beside `site/data/conditions/congestion.json`, as the page opens and after six choices (CAISO; 2024; every year held; a second place; another place and year): 3,752 of 3,752 at 1280 px, 538 of 538 at 390 px. Each of the two ranked tables is in the file's own order.

**What answers to the hand.** Six lists; a constraint's name (opens its grid); three charts under mouse and finger; three Chart and Table switches; an address naming nothing held opens on the defaults; the keyboard walks 75 stops with a focus mark each. The back button: row S1. 0.4 s to load; 390 px wide at 390.

No fault of its own.

Pictures: `docs/reviews/browser-read-2026-11-20/congestion/as-it-opens-1280.png` (SPP, 2026); `after-choices-1280.png` (CAISO, a constraint's grid over every year held).

### `/conditions`

Read with `runs/c620/n_conditions.mjs` and `runs/c620/n_conditions_file.py`.

**Five cases.**
1. *A trader on a tight day.* Is ERCOT running above its forecast? As the page opens: demand against the day-ahead forecast, hour by hour over the newest 35 days, then day by day. Answered; the chart runs to today.
2. *A reliability analyst.* How much was out of service in CAISO, and how many constraints bound? Chooses CAISO: six charts, each with a line. Answered.
3. *An event analyst.* ERCOT in Winter Storm Uri: the adder is drawn for February 2021. Answered.
4. *A planner comparing two operators.* ERCOT beside CAISO on one time axis. Answered, with two empty charts on ERCOT's side (row 1).
5. *A student.* What is not held? Each blank strip says why in a word (source needed, license needed, paused, not published, not read), and a table at the foot gives every operator's six strips. Answered.

**Figures.** The demand chart's own table (500 rows, two figures a row) is the file's demand and forecast, every figure. The other strips were read as charts: which hold a line, which are said blank.

**What answers to the hand.** Three lists and a day; the charts under mouse and finger (a card at four of four places on each of CAISO's six); the keyboard, 17 stops; 390 px wide at 390 for three views; 0.8 s to load. The back button: row S1.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | The page as it opens (ERCOT, the newest 35 days) | Two charts with axes and nothing on them, their seven ticks all reading "01-01 00:00": "Online reserve price adder" and "Hours the adder was above zero". The file's note says ERCOT's adder ended on 4 December 2025; the window holds no value. The same for "megawatts out of service" with CAISO in the September 2022 heat and with SPP and CAISO in Elliott | A strip with no value in the window drawn blank with its reason | filed (data request 568) |
| 2 | "Table" on the demand chart | 500 rows of the window's 841 hours, the oldest first | Withdrawn: my misread. The table pages 500 rows at a time and says "Rows 1 to 500 of 841" with Earlier and Later under it (the shared chart's own paging); the newest fourteen days are under Later. The data machine's answer to request 568 said so | not a fault |

Pictures: `docs/reviews/browser-read-2026-11-20/conditions/as-it-opens-1280.png` (ERCOT, demand against the forecast); `ercot-beside-caiso-1280.png`.

### The second landing (about 16:38 UTC), read on production at 17:05 to 17:25 UTC

- **`/conditions`, the answer to request 568.** Read again in the same ten views at 1280 px and three at 390 px: no chart is drawn with nothing on it any more (21 of 21 and 9 of 9 checks). As the page opens ERCOT has two charts, and the adder's strip says in words that no figure is held in the window and gives the file's last day. Row 1 above is fixed on production.
- **`/congestion`, its headings and labels changed.** The figures were set beside the file again: 3,752 of 3,752 at 1280 px, 538 of 538 at 390 px.
- **The variables table on the method pages** (the desktop's second window, chain 630; `runs/c620/n_codebook.mjs`). The codebook file names 475 method pages, 589 tables and 10,557 variables. At 1280 px, on the 473 pages that exist, every table is drawn and each of 10,443 variables' five cells is the file's (`site/data/codebook_methods.json`); no page scrolls sideways; none takes five seconds. At 390 px the variables are drawn as blocks inside the screen on the 24 pages sampled. All 614 method pages were opened again at 390 px: the same six scroll sideways as before the landing (mended on `wip/9601-method-pages-phone`), and none new.
- **Four method notes have no page** (`digest_scoring`, `forecast`, `roundup_selection`, `thesis_builder`: each answers "No page at this address"); none is linked from `/data`, so no reader is sent to them. Two of them have variables in the codebook file that are therefore never drawn. Noted.

Picture: `docs/reviews/browser-read-2026-11-20/codebook/variables-table-1280.png` (a method page's variables).

### The third landing (17:47 UTC), read on production at about 18:00 UTC

- **`/conditions`, "the window at a glance"** (`runs/c620/n_glance.mjs`): under each operator, the day of each strip's highest figure in the window. Each line was recomputed here from the operator's file and the window the page names, for seven views (ERCOT as it opens; CAISO; SPP beside CAISO; ERCOT in Uri; CAISO in the September 2022 heat; PJM beside MISO; ERCOT on a chosen day): 23 of 23 checks at 1280 px, 30 of 30 at 390 px, no sideways scroll. As the page opens: "Highest peak demand: 65,888 MW, on 2026-11-02".
- **`/congestion`**, whose table figures now carry keys into the page file: the figures set beside the file again, 3,752 of 3,752 at 1280 px and 538 of 538 at 390 px.

Picture: `docs/reviews/browser-read-2026-11-20/conditions/at-a-glance-1280.png`.

### `/states`, the answer to data request 563

On production after the landing, Texas's last section reads "Not held for this place: S.B. 6 was found but is withheld: its text was not read on a host that allows this reader ...". The page no longer reads as "Texas has no law".

