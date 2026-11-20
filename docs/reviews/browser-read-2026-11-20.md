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
| S1 | On a page with lists that submit themselves (`/queues/places`, `/curtailment/where-when`, and every page that draws the shared list of `site/components/AutoSubmit.tsx`): two choices made one after the other, then the browser's back button | The address and the page go back one choice; the list keeps the later choice. On `/queues/places` after TVA then Duke: the address reads `b=West:PacifiCorp`, the table shows PacifiCorp, the list "Queue B" reads Duke. On `/curtailment/where-when`: the grid shows 2025, the Year list reads 2019 | The list reads what the page shows | to fix (the shared list; the browser restores a form's last state on the way back, and the list takes its value only once) |
| S2 | A figure that is given only on hover, pressed with a finger at 390 px and reached with the Tab key | Nothing: the figure is the browser's own tooltip (a `title`). On `/curtailment/where-when` this is every figure of the hour by month grid (288 cells, none reachable by the keyboard, none shown to a finger); on the problem sets it is each figure's page file | A choice, not a fault of one page: it is ruling 13 of chain 504's note (should a reason also open on a tap? default: left as the site has it) | ruling (see "For Samuel's ruling") |

## 1. `/internal/findings`: the findings review page

Read for rows 423 to 428 of `docs/state/browser_reads_wanted.md` (`runs/c620/a2_findings.mjs`). No ruling button was pressed.

- **Seen:** the sheet of forty opens first, none drawn twice; the first block has its reader, title, sentence, figure, comparison, what would make it wrong, the audit's verdict, the four checks, the tables and the Stata and Python links; the chart's picture is drawn; the do-file opens in place and its "save" gives the repository's file under its own name; the bar of counts stays at the top while scrolling; each filter narrows; the search "Dominion" finds 3; "Show the next 40" adds forty; a withdrawn draft and a not-checked draft draw Approve disabled with the reason.
- **Time:** 4.6 s to the load event at 1280 px, 4.2 s at 390 px (614 drafts drawn by the server, 241,575 characters). Inside five seconds on this laptop, and the slowest page of the week.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | The page at 390 px | The page is 470 px wide: it scrolls sideways. A hunt's caption draft (a box of session 233) holds a long word that does not break | 390 px | to fix |

Picture: `docs/reviews/browser-read-2026-11-20/findings/` (added with the fix).

## 2. The four whole-country problem sets, and 11. the fifth (`your-own-balancing-authority`)

Read for rows 431 to 437 (`runs/c620/a2_sets.mjs`): every answer opened at both widths.

- **Seen:** each figure the rows name is on the page at 1280 and 390 px; each of the 503 figures of the five sets names its page file and path on hover; each set's `data.csv` answers with one row a figure; the index lists ten sets, each with the edition of 20 November; no sideways scroll with every answer open.
- **Against the pages the sets send a student to:** Elliott's page gives Tennessee the same highest hour (33,225 MW at 2022-12-24 01:00 UTC) and baseline (19,830 MW) as the storm set.

| # | What was done | What was seen | What should be seen | State |
|---:|---|---|---|---|
| 1 | "What is under the ground and in the wind", the worked example: "switch on Global Horizontal Irradiance; the legend runs from its lowest to its highest value", then the legend on `/map?tab=resources` | The set: lowest 2.81, highest 6.50 kWh/m2/day, 2.32 times. The map's legend: 1.6 to 6.9. The map widens a layer's legend to hold Alaska's and Hawaii's parts; the set reads the contiguous states' range from the list of layers. Question 2 uses the same 6.50 | The set and the map give a student the same two numbers | to fix |
| 2 | The same set, question 3: the wind legend's top | The set: 13.58 m/s. The map's legend: 13.6 (one decimal) | The same figure; the legend rounds | noted |

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
| 1 | The mouse on any authority at the hour the map opens on, then the slider stepped back | "Demand: not held for this hour" from 2026-11-18 04:00 back to 2026-11-16 00:00 UTC, for every authority; ERCOT's last figure is 52,838 MW at 2026-11-15 22:00. The line under the map says "Demand of the seven ISOs: newest hour 2026-11-20 08:00 UTC". The live set's demand ends on 15 November 23:00 UTC (read at 11:18 UTC on 20 November) | Demand for the hour shown | filed (data request 565) |
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

