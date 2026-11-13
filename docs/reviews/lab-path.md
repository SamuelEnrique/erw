# The lab's path, click by click (first walk, 6 November 2026)

Energy Research Warehouse (ERW), session 1499, chain 158 (`queue/done/158-day-6-november-code-replications-explorers-paths.md`). The path a lab's energy team takes when it asks what power will cost a datacenter, where, and how soon. It covers the datacenter tool, its All grids tab as the desktop's chains leave it, the datacenter tracker as the personal laptop's chains leave it, and Ask. Each page was read as it stood at the hour of the walk: another chain is changing the All grids tab and the tracker, so this walk records them as they were.

**How it was walked.** On 6 November 2026, about 10:03 UTC, on a local production build of main at `04623251`, in the internal view, in a real browser (`site/scripts/walk-paths-1497.mjs`; the steps in `docs/reviews/paths/lab-1497.json`). Each step has its screenshot of the first screen at 1280 px, and the first also at 390 (`docs/brand/review-1497/lab-<step>-1280.png`, `lab-01-390.png`). Every figure below is the page's keyed figure.

## Step 1: What a datacenter pays, as it opens

- Address: `/cost-of-power` (ERCOT's LZ_NORTH, a flat load bought in real time, 100 MW).
- What the reader sees first: the last twelve months (November 2025 to October 2026) cost **USD 34.07 per MWh**, USD 29.84 million for 100 MW, **USD 0.0691 a GPU-hour**. Beside them, the hub average's day-ahead basis band of November 2025: p10 -6.93, median -0.42, p90 8.66.
- Shots: [lab-01-1280.png](../brand/review-1497/lab-01-1280.png), [lab-01-390.png](../brand/review-1497/lab-01-390.png).
- Broken: none (at 390 px the page fits: scroll width 390).
- The replication a reader runs: `replication/datacenter/` (14 of 14 of the page's figures since session 1523; the carbon over the hourly window, which session 1491 left open, was the live set's moving window).

## Step 2: bought day-ahead

- Address: `/cost-of-power?buy=da`.
- What it shows: **USD 35.70 per MWh**, USD 31.27 million, USD 0.0724 a GPU-hour.
- Shot: [lab-02-1280.png](../brand/review-1497/lab-02-1280.png). Broken: none.

## Step 3: the All grids tab

- Address: `/cost-of-power?view=allgrids` (the desktop's chains 155 and 157 are wiring it; read as it stood).
- What it shows: one table of 48 hubs and zones and ERCOT's nodes, each with energy, transmission, capacity and the time to connect. CAISO's NP15, for one: energy 34.07 USD per MWh day-ahead and 32.67 in real time; "transmission: not held"; "no capacity market" (California has none); connection, the median months for generation in CAISO. 41 cells say "license needed": the held grids, as the hold of 21 October says.
- Shot: [lab-03-1280.png](../brand/review-1497/lab-03-1280.png). Broken: none read here. The tab's open cells are the desktop's to fill.

## Step 4: the datacenter tracker, the facilities

- Address: `/datacenters` (the personal laptop's chain 156 is extending the tracker; read as it stood).
- What it shows first: ERCOT's large-load interconnection status (the report of 19 June 2026): 8,927 MW asking to energize, observed peaks of 3,900 and 3,675 MW; and the month before, 9,062 MW. 5 notes "license needed".
- Shot: [lab-04-1280.png](../brand/review-1497/lab-04-1280.png). Broken: none.

## Step 5: the tracker by grid

- Address: `/datacenters?view=grids`.
- What it shows first: ERCOT, 2 sites (2 stating MW, 191.26 MW asked); 1,169 active queue positions, 298,606 MW; the power price at the Houston zone 34.01 and at Austin Energy's 39.01 USD per MWh.
- Shot: [lab-05-1280.png](../brand/review-1497/lab-05-1280.png). Broken: none.

## Step 6: Ask the warehouse

- Address: `/ask`. The page was read without asking a question: no model call was made in this walk.
- What it shows first: the Lower 48's demand at its newest hours (495,243 MW at 23:00 UTC on 4 November; 499,384 a week before), generation and carbon beside them; the form to ask. The page's first heading is "The Lower 48 states", the panel's, above the form.
- Shot: [lab-06-1280.png](../brand/review-1497/lab-06-1280.png). Broken: none. The board's five questions, asked through the same loop by session 1486 that morning, were 5 of 5 right.

## What the walk found

1. At 390 px the page fits (scroll width 390, measured with a phone's device metrics; a first reading of 481 px with a headless window alone was the script's, and corrected).
2. **For the owner's reading**: the Ask page's first heading is the data panel's ("The Lower 48 states"), not the page's own name. A reader arriving from the menu sees a grid's name first.
3. Nothing else: every step loaded with no error, and every figure read is the page's keyed figure.

## Feedback

To be filled when a lab's team has walked it: one row a remark, with the step.

| Date | Who | Step | What they said | What was done |
|---|---|---|---|---|

## Walked 13 November 2026 (session 1885)

Session 1885 walked the lab's path again, click by click, at about 00:11 UTC on 13 November 2026 (the file times of its records), in the internal view, on a local production build of the chain's newest code (main at `ad73c5e9b` plus the unlanded board, periodicals and records branches) served on port 3885. This walk takes the path in the order a lab's team now meets it: the datacenter tracker first, then a load zone's cost from the tracker's own link, the All grids tab, and the grid page. It has thirteen steps; where a step is one of the six of 6 November, it says which, and where the page has moved since, it says so. The clicks were made in a real browser by `runs/s1885/walk.mjs` (`node runs/s1885/walk.mjs http://localhost:3885 lab 1280`); every step's record (address, the keyed figures in view, the visible text) is in `runs/s1885/lab-1280.json`, and its shot in `runs/s1885/shots/lab-<step>-1280.png` (`runs/` is not in git: the shots stay on the code machine). The first walk's steps 11 to 13 misclicked: the script looked for a link to `/grid?grid=ercot` that the Grid menu does not hold, found none, and stayed on the All grids tab, so `lab-11-grid-ercot-1280-misclick.png`, `lab-12-grid-built-1280-misclick.png` and `lab-13-grid-datacenters-1280-misclick.png` show that tab, not the grid page. Steps 11 to 13 were walked again from the All grids tab (`node runs/s1885/walk.mjs http://localhost:3885 lab2 1280`; `runs/s1885/lab2-1280.json`, shots `lab2-<step>-1280.png`), and the steps below are the second walk's. No page threw an error; every page is 1265 px wide in a 1280 window (the scroll bar), none wider. Every figure quoted is the page's own. `/ask` was not opened and no question was asked.

### The datacenter tracker

- **01.** Infrastructure menu, **Datacenters** (address `/datacenters`; the first walk's step 4). The page opens on the hold: "All 458 rows of datacenter_facilities are held from 2026-10-21: the facilities rest on news stories and the operators' own pages, whose terms ask for permission, which is not yet recorded. So the list, the rollups by grid and operator, the timeline and the charts are not drawn". Below it, ERCOT's large-load report, as on 6 November: "By ERCOT's report of 19 June 2026, 8,927 MW of large load had its approval to energize, and ERCOT had observed 3,900 MW of it running (44 percent). On 28 May 2025 the two figures were 6,874 and 3,489 MW." Served at one moment **3,675** MW. Shot: `lab-01-tracker-1280.png`.
- **01b.** Scroll to ERCOT's figures. Under the three cards: "These are the newest figures ERCOT has stated, of 19 June 2026: on 3 August 2026 ERCOT paused approvals to energize datacenters and virtual currency mining facilities of 75 MW or more, and its Batch Zero study, and no status update since states these figures (ERCOT's deck to TAC of 26 August 2026, Batch_Zero_Update_TAC_08262026.pptx". The chart runs one point a report, 2025-05 to 2026-06. Shot: `lab-01b-tracker-ercot-1280.png`.
- **02.** Click **By grid** (`/datacenters?view=grids`; the first walk's step 5). "Sites from public sources, by grid and zone, against the queue and the price": ERCOT, **2** sites, **2** stating MW, **191.26** MW asked (as on 6 November); **1,159** active positions in the queue, **308,488** MW (1,169 and 298,606 on 6 November); a flat load over the last twelve months USD **34.02** at the Houston load zone to **39.01** at Austin Energy's (34.01 and 39.01 on 6 November). "Not read: the queues of NYISO, MISO, ISO-NE, held while their operators' terms ask for a license." Shot: `lab-02-bygrid-1280.png`.
- **03.** Scroll to "ERCOT: what a flat load paid, by year". Cheapest zone, North (the calculator's default), dearest, each year 2018 to 2025, then "Last 12 months, Nov 2025 to Oct 2026": **34.02**, **34.07**, **39.01**; 2021 reads 146.46, 150.61, 151.76. Shot: `lab-03-bygrid-years-1280.png`.
- **04.** Scroll to "The facilities against each grid". Seven grids, nine columns, and every cell of every row reads "license needed" with note 1, "The facilities rest on news stories and the operators' own pages", the Peak hour MW and Capacity MW columns included, and ERCOT's Reserve margin too; the other grids' margins read "not held" with note 2, "A grid's reserve margin is held for ERCOT only (its Capacity, Demand and Reserves report...)". The line under the table says the peak and the capacity are each grid's own, "(EIA-930 and EIA-860M, grid_peak_vs_capacity)" (fault 2). Shot: `lab-04-bygrid-facilities-1280.png`.
- **05.** Click **Facilities**, scroll to "What a flat load paid in ERCOT, by load zone". Eight zones, each "Nov 2025 to Oct 2026": North **34.07** (real time, the calculator's default, as on 6 November), Austin Energy **39.01** (day-ahead), CPS Energy **38.99**, Houston **34.02** (real time), Lower Colorado River Authority **38.64**, Rayburn **35.98**, South **34.17** (real time), West **35.35** (real time). "The ERCOT section reads the site's own copy of the table, built 2026-11-06." Shot: `lab-05-zones-1280.png`.

### What a datacenter pays, at the West load zone

- **06.** Click the link **West load zone** (`/cost-of-power?grid=ercot&region=LZ_WEST`; the first walk's step 1 opened North). "A flat 100 MW load at LZ_WEST in ERCOT, buying real time, paid USD 35.35 per MWh over the last twelve months, USD 30.97 million in all: USD 0.0717 per GPU-hour for power alone." 876,000 MWh, "Nov 2025 to Oct 2026"; a bad month USD **47.47** (December 2025), of 36 held from November 2023 to October 2026; 100 MW powers **49,310** GPUs at 1.3 kW and an overhead of 1.56. Shot: `lab-06-cop-west-1280.png`.
- **06b.** Scroll to **Price years**. "What will it cost": market energy **35.35**; the hub beside it, HB_WEST, **31.04** (USD 27.12 million), "the load zone is 4.31 per MWh above its hub"; wholesale transmission, all of ERCOT, USD **7.83** a MWh for 2025 (approved) and **8.62** for 2026 ("filed, not approved"); "Capacity charges: None: ERCOT is an energy-only market"; the resource nodes' day-ahead basis to the hub average **-7.85**, **0.33**, **6.84** at the 10th, median and 90th, "Not added to any figure"; delivery charges in Texas for a flat load, total with the conditional lines: Oncor **8.81**, CenterPoint **7.67**, AEP Texas **8.39**, Texas-New Mexico Power **7.09**. Shot: `lab-06b-cop-west-years-1280.png`.
- **07.** Scroll to "Will the power be there?". "Over the last twelve months, Nov 2025 to Oct 2026, the price at LZ_WEST in ERCOT was at or above USD 1,000 per MWh in 3 hours: January 2026 (3), between 07:00 and 22:00 US Central standard time. A flat 100 MW load paid USD 339,565 in them", USD 1,131.88 a MWh on average. ERCOT's own signal, the reserve adder at USD 100 or more: **0** hours, the adder "published it until 4 December 2025 and no longer: this count covers 816 hours". Shot: `lab-07-cop-power-1280.png`.
- **08.** Scroll to "How soon?". ERCOT's report of 19 June 2026: **8,927** MW approved, **3,900** running, "the approved figure grew by 2,053 MW since the report of 28 May 2025"; new submissions by 13 March 2026: **137** requests, **140,000** MW; "No wait is estimated: ERCOT publishes none." Public documents state **67** figures (55 of megawatts, 12 of a wait) from 5 entities in 28 documents: the newest wait **60 days** (Public Utility Commission of Texas, 18 September 2026, Project 58481), the newest megawatt figure **22,000** MW (ERCOT, 17 September 2026); 91 public figures in Texas; 8 proceedings in motion. The reports table: 19 June 2026 8,927, 3,900, 3,675; 21 May 2026 **9,062**, 3,900, 3,701 (6 November's "the month before, 9,062"); 24 April 2026 9,042, 4,008, 3,701. Shot: `lab-08-cop-soon-1280.png`.

### The All grids tab

- **09.** Click **All grids** (`/cost-of-power?view=allgrids`; the first walk's step 3). Three tabs, Your load, All grids, Grid by grid, and under All grids two, "Hubs and zones (48)" and "ERCOT nodes (873)". "Every hub and load zone the page's price files hold, and the grids they do not price: 48 rows." CAISO's NP15: energy **34.11** day-ahead and **33.16** real time (34.07 and 32.67 on 6 November); transmission **$11.03/kW-mo** (on 6 November "transmission: not held"); "no capacity market"; connect **100.00** months, "load: rule 2026-06, filed steps"; headroom **+5.18** percent, 8,276 MW coming, capacity 106 percent above peak, reserve margin 30.8 percent (summer 2026); 94,096 MW signed; 2030 peak forecast **-2,442** MW since the 2024 filing; **73,848** MW in queue; carbon **194.35** kg (428.46 lb); Pacific Gas & Electric Co. **325.37**, -8.61 percent; all-in "not held". SP15: **30.27** and **29.72**, transmission "not held". Shot: `lab-09-allgrids-1280.png`.
- **10.** Scroll to the ERCOT LZ_WEST row. Energy **37.21** day-ahead, **35.35** real time (the step 06 figure); transmission **7.83** (firm 7.83, off 0.00); "no capacity market"; connect **45.80** months, "load: rule 2026-09, 8,927 MW approved"; headroom **+5.21** percent, 24,269 MW coming, capacity 97 percent above peak, reserve margin 11.43 percent (summer 2027); 132,566 MW signed; 2030 peak forecast "+ 0.4 MW since the 2024 filing" (a figure the owner may want checked against ERCOT's filings; not checked here); **298,606** MW in queue (fault 1); carbon **332.87** kg (733.86 lb); TXU Energy Retail Co, LLC **73.57**, +9.44 percent; all-in **45.03** (LZ_SOUTH beside it: 34.87, 34.17, all-in 42.69). The table scrolls sideways inside the page at 1280 px. Shot: `lab-10-allgrids-west-1280.png`.

### The grid page

- **11.** Grid menu, **The grid** (`/grid`; second walk). The page's head is "The Lower 48 states". "In the hour starting 2026-11-11 23:00 UTC, the latest EIA has published, the Lower 48 states used 488,034 MW, less than the 495,243 MW of the same hour a week earlier" (495,243 was the newest hour, 4 November, on 6 November's `/ask`). Natural gas **215,277** MW of **484,045** generated; **363.91** kg of CO2 a MWh in the hour starting 2026-11-10 23:00 UTC. The three cards: Demand **488,034** MW; Net export "by grid MW" (fault 3); Carbon intensity **363.91**. Beside them the Ask box: "the 45 tables held for a license are refused by name"; "at most 10 questions per hour". Shot: `lab2-11-grid-1280.png`.
- **11b.** Click **ERCOT** on the grid row (`/grid?grid=ercot`), scroll to "What it costs". ERCOT Hub Average day-ahead **33.74** (2026-11-13), real time **82.54** (2026-11-11), day-ahead peak **29.50**, off-peak **42.22**, the 30-day mean **34.79**, from `price_board_latest` and `price_board_peak_offpeak`. Shot: `lab2-11b-grid-ercot-1280.png`.
- **12.** Scroll to "What is being built". Waiting (active), active MW, completed: storage **616**, **118,354.40**, 212; solar **347**, **85,526.60**, 249; natural gas **112**, **72,589.10**, 33; wind **74**, **27,667.70**, 83; hybrid 2, 2,656.50, 0; hydro 2, 1,311.60, 0; other 4, 200, 0; petroleum 1, 132, 0; unknown 1, 50, 0. The nine kinds add to the tracker's 1,159 positions and 308,488 MW of step 02. Shot: `lab2-12-grid-built-1280.png`.
- **13.** Scroll to **All datacenters**. "Datacenter facilities mapped to ERCOT model-extracted license needed facilities; license needed MW where a source states it." Under it, "In the news": "license needed scored stories since 2026-10-30 whose headline names ERCOT or Texas or whose region is Texas. No story in the last 14 days matched." (fault 4). Shot: `lab2-13-grid-datacenters-1280.png`.

The first walk's step 2 (bought day-ahead, `?buy=da`) was not walked; the All grids row gives LZ_WEST's day-ahead beside its real time (step 10). The first walk's step 6 (`/ask`) was not walked; its Ask box is now beside the grid page's Lower 48 panel (step 11).

### Faults found

1. **All grids, step 10, against the tracker (step 02) and the grid page (step 12)**: ERCOT's rows read "298,606 MW in queue", while the tracker gives "1,159" active positions and "308,488" MW and the grid page's kinds add to the same; 298,606 is the figure the tracker gave on 6 November. Should: one queue figure on the three pages. The data machine's: the tab reads the page's file from `iso_queue_snapshot_summary` (`queueCell` in `site/lib/siting.ts`), which still carries the older figure while `ercot_interconnection_queue` carries the newer. State: data machine.
2. **Tracker by grid, step 04**: "The facilities against each grid" prints "license needed" (note 1, the facilities' hold) in the Peak hour MW and Capacity MW columns of every grid and in ERCOT's Reserve margin, though the line under the table names them as each grid's own figures "(EIA-930 and EIA-860M, grid_peak_vs_capacity)" and note 2 says ERCOT's margin is held. Should: the grid's own columns drawn, only the facility columns held. Site code fix. State: ruling (the same cells are row 4 of `datacenter-faults-2026-11-11.md`, the owner's: whether a grid's public columns show while its facility counts are held). Session 1898 printed them (`a05a17e9b`, landed at `b1bc8829f`); session 1905 put the default back (footnote 1) until the owner rules.
3. **Grid page, step 11**: the Lower 48's second card reads "Net export" then "by grid MW": words where the figure goes, with the unit after them. Should: words without a unit (or the card left out for the Lower 48). Site code fix. State: fixed (`9c5745d4b`, session 1898: the card takes its MW only beside a figure).
4. **Grid page, step 13**: "In the news" holds the count ("license needed scored stories since 2026-10-30") and then says "No story in the last 14 days matched", which reads as a search of the held table that found nothing. Should: the stories said held, with no empty-result line. Site code fix. State: fixed (`6482a971a`, session 1898: held, the section is one sentence of the hold, no count and no empty-result line).

## Walked again 13 November 2026, the fixed steps (session 1904)

Main at `b1bc8829f`, the local build on 3904, internal view, 1280 px (`runs/s1904/lab-1280.json`); steps 11 to 13 from session 1903's read of the same code on the gate's build, at 390 and 1280 (`runs/s1903/read.json`), since the walk's click on the Grid menu found no link (a page in review is a span in the fetched menu, not a fault of the page).

| Step | Session 1885 | Session 1904 |
|---|---|---|
| 04, the facilities against each grid (fault 2) | "license needed" in every grid's Peak hour MW and Capacity MW and in ERCOT's reserve margin | each grid's own figures: ERCOT "83,597" and "164,685", reserve margin "11.4% (summer 2027)", PJM "160,560" and "210,667", and so on for seven grids; the facilities' five columns and the share of peak still "license needed" (the facilities' hold) |
| 11, the Lower 48's second card (fault 3) | "Net export by grid MW" | "Net export by grid", then "The Lower 48 is the sum of its grids: the exchange of each."; ERCOT "Net import 219 MW" |
| 13, In the news (fault 4) | "license needed scored stories since 2026-10-30 ..." then "No story in the last 14 days matched" | "The scored stories are held for a license (license needed): the outlets' terms ask for permission and none is recorded yet, so this section shows neither their count nor their headlines." No empty-result line |

Fault 1 (ERCOT's queue on All grids) is the data machine's and reads as before. Step 04's reading is of the build before session 1905 put fault 2's default back: the cells are the owner's ruling (datacenter row 4).
