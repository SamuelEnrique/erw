# What a datacenter pays: every number, step by step

Energy Research Warehouse (ERW), session 190, 11 October 2026. Written for sign-off. Page: `/cost-of-power`. This note is written from the code, not from the older notes: `warehouse/derived/datacenter_page.py` (the builder of the page's files), `warehouse/derived/price_compare.py` (the reader of the price tables and the rule for an hour), and on the site `lib/datacenter.ts` (all the arithmetic), `lib/datacenterdata.ts` (the files) and `app/cost-of-power/`. Where the older note and the code differ, section 9 says so. The older note, [`datacenter_cost.md`](datacenter_cost.md), stays as the record of why each piece was built, of every source's terms and of the blocks this page borrows from other tools.

Downloads, the default case hour by hour: [erw_2026_datacenter_hourly.csv](/datacenter/erw_2026_datacenter_hourly.csv), [the Stata do-file](/datacenter/erw_2026_datacenter_replication.do) and [its Python mirror](/datacenter/erw_2026_datacenter_replication.py). Section 8.

**The default case**, used for every example below: ERCOT, the North load zone (`LZ_NORTH`), a flat load of 100 MW, bought in real time, 1.3 kW per GPU, an overhead ratio of 1.56. With the page's files built on 10 October 2026 the page shows: USD 33.73 per MWh over the last twelve months (October 2025 to September 2026), USD 29.55 million for 876,000 MWh; a bad month of USD 37.88 per MWh (August 2026, of 36 months); USD 0.0684 per GPU-hour, 49,310 GPUs; the hub beside the zone (`HB_NORTH`) at USD 32.51, so the zone is 1.22 above its hub.

**The files these figures are of** (session 199). The page's files are rebuilt every day and the page shows the day's; the figures quoted in this note are those of the build of 10 October 2026 and stay so. What they need of that build is kept in `docs/methods/figures/2026-10-10/datacenter_pays_inputs.json` (the default case's months, and the hours of 2025 and 2026 that a flexible load's figures need), and `tests/test_session190.py` recomputes them from that file with the page's own library.

**The flexible example**, used in section 5: the same load set to turn off in 100 hours a year. The page shows USD 31.46 per MWh, 2.27 less than a flat load, and USD 29.72 "if perfectly foreseen" (4.01 less).

## 1. The order of computation

1. **The price tables** are written by their connectors (the daily run, and the two history pulls of sessions 138 and 140). Section 3 names each.
2. **The builder** (`datacenter_page.py`) reads every public hub and zone price table, turns each series into one price an hour, places the hours on the grid's standard time and writes one file a grid and year under `site/data/datacenter/`, with `index.json`. It makes no request and writes no table. It runs on the GitHub runner on Saturdays (`warehouse/refresh_supply.sh`) and in the data machine's run (`warehouse/run_data_machine.sh`, which is registered nowhere: section 10, item 4). A build is merged into the files already kept: an hour the new build holds is the new build's, an hour only the kept file holds is kept.
3. **The page, on each request**, reads the grid's files and computes every cost figure it shows with `lib/datacenter.ts`, per MW, and multiplies by the reader's size. Nothing is read from the database for the cost. The contract computes in the browser.
4. **The other three questions** (will the power be there, how clean, how soon) show headline figures of other tools, read from those tools' own files. Three figures there are this page's own: the tight hours, the hours of them the load was off, and the load's own hours against the grid's carbon-free share (sections 4.7 and 4.8).

**The checks.** `site/scripts/check-datacenter.mjs` recomputes the summary's figures with the same library from the same files and compares them with what the built page printed, for a flat load, a load off in 100 hours bought day-ahead and a shifting load in California. `check-values.mjs` checks the 83 values of the view "Grid by grid" against the live set. This session's test recomputes the default page from the CSV alone, and the flexible example by an independent implementation of the rule (section 8).

## 2. The reader's inputs

All are in the address, each bounded and defaulted (`inputsOf`). The contract's two terms are not in the address: they live in the page's memory and are never sent.

| Input | Default | Bounds | What it changes |
|---|---|---|---|
| `grid` | `ercot` | `ercot`, `caiso`, `nyiso`, `isone`, `spp`. An address that names `miso` or `pjm` opens ERCOT's prices; only "How long a large load waits" and "Rules in motion" follow the grid named | the files read |
| `region` | the grid's main region: `LZ_NORTH`, `TH_SP15_GEN-APND`, `N.Y.C.`, `.H.INTERNAL_HUB`, `SPPNORTH_HUB` | the grid's hubs and zones in the index; any other value opens the main region | the price series |
| `mw` | 100 | 0.1 to 10,000 | every US dollar and MWh figure is the per-MW figure times `mw`; per-MWh figures do not move |
| `run` | `flat` | `flat`, `hours`, `share`, `shift` | how the load runs (section 5) |
| `n` (with `hours`) | 100 | 0 to 8,784, rounded to a whole number | hours a year the load may be off |
| `pct` (with `share`) | 5 | 0 to 100 | percent of hours the load may be off |
| `shift` (with `shift`) | 20 | 0 to 50 | percent of each day's energy moved |
| `buy` | `rt` | `rt`, `da` | the market the load pays. When the address names no market and real time holds no twelve counted months but day-ahead does, day-ahead is shown |
| `gpu` | 1.3 kW | 0.05 to 20 | the GPU-hour figure and the GPU count only |
| `pue` | 1.56 | 1 to 3 | the same two |

Anything outside its bounds is clipped; anything unreadable takes the default.

**Session 195: `gpu` and `pue` are the scenarios'.** "Your load" no longer holds a power per GPU and an overhead ratio. Scenario A of "Scenarios A and B" (4.14) holds them, with the same defaults and bounds, and the page's GPU-hour figures read them from scenario A. In an address written before the session the two names are still read, once, as old names of both scenarios' assumptions (`battery_earns_algorithm.md`, section 11.1, "The block the three pages share"), because "Your load" was the default of both. Everything this note says of `gpu` and `pue` below holds with scenario A's values in their place.

## 3. The price of an hour

**Tables read** (`TABLES` in the builder; all public in `coverage.csv`): `iso_hub_prices_history`, `ercot_all_hub_prices_history`, `ercot_zone_prices_history`, `iso_zone_prices_history`, then the daily tables `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `isone_dam_zone_prices`, `isone_rtm_zone_prices`, `isone_rtm_zone_prices_hourly`, `nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices`. Columns used: `entity`, `variable`, `ts_utc`, `value`, `freq`. Rows from 1 January 2015.

- **Which rows.** A row is day-ahead when its `variable` is `lmp_dam` or `spp_dam`, real time when it is `lmp_rtm_15m_mean`, `spp_rtm` or `lmp_rtm`. A row held in two tables (the same entity, market, frequency and time) is read once, from the table earlier in the list.
- **Not read.** A table whose license in `coverage.csv` is not public (ISO-NE's zone history, by the owner's ruling of 7 October 2026). A publisher in `paused_sources.csv` (MISO): its regions are named in the index with the words "paused while terms are reviewed" and no number. PJM: no hub or zone price is held; the index gives the words "licensed source needed".
- **An hour.** A day-ahead price is hourly and is taken as it is. A real-time price at 15-minute frequency becomes the mean of the hour's four prices, and the hour is held only when all four rows are there. Where a market is held at two frequencies (ISO-NE's real time, 15-minute and hourly), the one that gives more hours is used whole and the other not at all. The hour's price is rounded to the cent.
- **Standard time.** The hour is placed by UTC less the grid's standard offset (ERCOT and SPP 6 hours, CAISO 8, NYISO and ISO-NE 5), with no daylight saving shift. Every day has 24 hours, a year 8,760 or 8,784. In summer an hour on this page starts one hour before the clock on the wall says.
- **Nothing is filled.** An hour not held is null in the file and is left out of every sum.

**For the default case:** `LZ_NORTH` is read from `ercot_zone_prices_history` (`entity` `ercot:LZ_NORTH`; `market` `ercot_rtm`, 15-minute, ERCOT report NP6-785-ER; `ercot_dam`, hourly, NP4-180-ER), 1 January 2015 to 3 October 2026. `HB_NORTH` is read from `ercot_all_hub_prices_history` to 25 August 2026 and from `iso_rtm_hub_prices` after it (ERCOT NP6-905-CD).

**Checked against the tables in this session** (the tables as they stand on the code machine, read as text, with none of the builder's functions): each of the 103,055 hours of the default case equals the tables' own value to half a cent, for the zone's real-time price (412,220 rows, four in every hour, none blank), its day-ahead price and the hub's real-time price. No hour is in one and not the other. `runs/session190/tables_check.out`.

## 4. Every number on the page, in the order the page shows it

**Session 228: the page answers its four questions**, each computed for the load the reader describes: "What will it pay?" as before, then "Will the power be there?" (4.15), "How clean?" (4.16) and "How soon?" (4.17), then the two of the decisions, "Which option is better?" and "What matters most". The three answers follow the page's pattern (one sentence with the number, three numbers, one table, scenario B's answer beside A's where they differ); every number carries a check key and is in the downloads (`months.csv`: the scarce hours and the grid's intensity of each month; `tables.csv`: the tables `scarce_hours`, `carbon` and `large_load`) and in the replication files (section 8). Nothing of "What will it pay?" moved.

**Session 213 (the owner's chain prompt of 12 October 2026): the page asks the battery page's three questions**, and this section's order is the page's order until then. What the page draws now: (1) "What will it pay?": the summary sentence (4.2), the three headline numbers (4.3 to 4.5), the cost chart by year and the table "What will it cost" (4.6, its delivery rows among them), one sentence of what the model cannot see (below), the links to the grid's own pages, and the two CSV downloads. (2) "Which option is better?": scenarios A and B (4.14), with the contract's share of the energy and its price as two of their assumptions (4.10 is how the contract was computed until this session). (3) "What matters most": the sensitivity chart (4.14) with one line on how to read it. Into the CSV downloads, computed as this section says, by `site/app/cost-of-power/model.ts`, which the page and the downloads share: `/cost-of-power/months.csv` holds every year and every month (4.11's first two folds: the flat price, this load's, the foreseen price, the hours off, the cost for the size, the hours held); `/cost-of-power/tables.csv` holds, in long form (table, row, column, value, note), "Will the power be there" (4.7), "How clean" (4.8), "How soon" (4.9) with the waits of a large load by stage and the rules in motion (`datacenter_cost.md`), every region of the grid over its own last twelve months, the Commission's transmission charge matrix (4.11), and New York's load in line request by request where NYISO's terms allow it (4.9). Gone outright: the standalone contract panel and "With your contract" (4.10). The view "Grid by grid" (4.13) and the source line (4.12) are as they were. Each download takes the page's status: in review, a visitor is answered 404. Nothing in the arithmetic changed: at a contract share of 0 every number is what it was, to the bit.

<a id="cannot-see"></a>

**What the model cannot see** (the one sentence under the cost table says the first of these; the page's hover reasons and `datacenter_cost.md` say the rest):

- Market energy at the region's hub or zone price alone: no delivery, transmission, capacity, ancillary or retail charge is added (Texas's tariff charges stand in their own rows of the table, never added; the scenarios' "delivery and other charges" is the reader's own figure).
- The load buys every hour at the hour's price, with no hedge, no block purchase and no basis to its own node; a flexible load follows a rule decided before each hour (section 5.1), and the foreseen figure beside it is a bound, not a plan.
- A contract (4.14) is a share of the energy at a fixed price for every year counted: no shape, no settlement point, no collateral, no term shorter or longer than the years counted.
- The years counted repeat the last twelve months, changing by one rate (4.14): not a forecast and not a valuation; no tax, no outage, no growth of the load itself.
- The grid's own figures (4.7 to 4.9) are the other tools' and the operators' as published, for the grid as a whole, not for the load's point of connection.

"The months" below are the months of the region and market for the load (section 4.1). Every sum is per MW; `MW` is the reader's size.

### 4.1 Months, and which count

For each calendar month of standard time (`monthsOfYear`), over the hours whose price p is held, with the load's weight w in each hour (1 for a flat load; section 5 for the others):

- `due` = the month's calendar hours, 24 times its days (672, 696, 720 or 744);
- `held` = the number of hours with a price;
- `flat` = sum of p: what a flat MW paid, USD;
- `cost` = sum of p x w: what a MW of this load paid, USD;
- `energy` = sum of w: what it consumed, MWh;
- `down` = the number of hours with w = 0.
- **A month counts** when `held >= 0.95 x due`. A month under 95 percent is drawn pale in the folds and is in no headline figure. A month with no hour held is not a month.

**A span of months** (`span`): flat price = sum of `flat` / sum of `held`; the load's price = sum of `cost` / sum of `energy`; both USD per MWh. A span weighs every hour the same, so a 31-day month weighs more than February.

**The last twelve months** (`lastTwelve`): the newest counted month whose eleven months before it all count; those twelve. When no such twelve exist the figure is the placeholder "not held yet", whose hover gives the date the region is held from.

### 4.2 The summary sentence

"A flat 100 MW load at LZ_NORTH in ERCOT, buying real time, paid USD 33.73 per MWh over the last twelve months, USD 29.55 million in all: USD 0.0684 per GPU-hour for power alone."

- **Per MWh** = the last twelve months' sum of `cost` / sum of `energy`.
- **In all** = sum of `cost` x MW, printed in millions or billions with at most two decimals.
- **Per GPU-hour:** 4.5.
- A load that is not flat adds "USD s per MWh less than a flat load (USD h if perfectly foreseen)": s = the span's flat price less the load's price, under the rule; h = the same difference for the foreseen load over its own last twelve months (section 5).

**Worked example, the default case.** The twelve months, each whole:

| Month | Hours | Sum of the hourly prices, USD | USD per MWh |
|---|---|---|---|
| 2025-10 | 744 | 23,207.95 | 31.19 |
| 2025-11 | 720 | 23,340.43 | 32.42 |
| 2025-12 | 744 | 25,994.28 | 34.94 |
| 2026-01 | 744 | 39,815.30 | 53.52 |
| 2026-02 | 672 | 13,610.00 | 20.25 |
| 2026-03 | 744 | 17,035.05 | 22.90 |
| 2026-04 | 720 | 28,221.84 | 39.20 |
| 2026-05 | 744 | 20,020.48 | 26.91 |
| 2026-06 | 720 | 22,256.97 | 30.91 |
| 2026-07 | 744 | 22,757.86 | 30.59 |
| 2026-08 | 744 | 28,184.74 | 37.88 |
| 2026-09 | 720 | 31,020.15 | 43.08 |
| **Twelve months** | **8,760** | **295,465.05** | **33.73** |

295,465.05 / 8,760 = 33.7289, shown 33.73. Times 100 MW: USD 29,546,505, shown "29.55 million". Energy: 8,760 x 100 = 876,000 MWh.

### 4.3 Headline 1: last twelve months, market energy, USD per MWh

As 4.2. The note under it: the cost in USD, the energy in MWh (sum of `energy` x MW) and the first and last month. For a load that is not flat the note adds the foreseen figure.

### 4.4 Headline 2: a bad month

- **The window** (`last36`): the 36 calendar months that end with the last month of the last twelve months (when there are no twelve months: with the newest counted month). Of them, the months that count.
- **The month** (`badMonth`): those months sorted by cost per MWh (`cost` / `energy`), dearest first, ties by the earlier month; the month at position ceiling(0.1 x N), counted from 1. A real month (nearest rank), not an interpolated value. One month in ten cost that or more.
- The note names the month, N, and the first and last month of the window that count. With fewer than 36 months held the figure is taken over those held and N says how many.

**Worked example.** N = 36 (October 2023 to September 2026, all counted). ceiling(3.6) = 4. The four dearest: January 2026 (53.52), September 2026 (43.08), April 2026 (39.20), **August 2026 (37.88)**. The cheapest of the 36 was February 2024 (13.94). In the table the same month in dollars: 28,184.74 x 100 = USD 2,818,474, shown "2.82 million".

### 4.5 Headline 3: power per GPU-hour

- **USD per GPU-hour** = price per MWh x kW per GPU x overhead ratio / 1,000. The price is the last twelve months' price of the load (4.2). Default: 33.7289 x 1.3 x 1.56 / 1,000 = 0.068402, shown 0.0684.
- **GPUs** = MW x 1,000 / (kW per GPU x overhead ratio). Default: 100,000 / 2.028 = 49,310.
- Energy at the market price and nothing else: no delivery, no demand or capacity charge, no hardware. For a load that turns off it is the price of the hours it runs.

**Session 195: the three headline numbers are scenario A's rows** (4.14), computed in the browser as A is changed (`site/app/cost-of-power/LoadHeadline.tsx`). Headline 1 is the market energy of the way scenario A runs; headline 2 is that way's bad month; headline 3 is A's row "Power per GPU-hour", at A's power per GPU and overhead ratio, with A's other charges when it has any. At the defaults A runs as "Your load" describes and has no other charge, so the three are what they were (33.73, 37.88, 0.0684). When A runs the other way, the first number's note says so, and that the sections below are the load as "Your load" describes it; when A has other charges, the third number's note states them. The power per GPU-hour of the summary sentence (4.2) and of "What will it cost" (4.6) prices the load as "Your load" describes it, at A's power per GPU and overhead ratio.

### 4.6 The chart and the table "What will it cost"

- **The chart, cost by year.** For each calendar year, the span of its counted months (`years`): the flat price, and for a load that is not flat the load's price under the rule and the foreseen price. A year is complete when all twelve months count; otherwise it is hatched and holds its counted months only. Default: 24.04 (2015), 21.68, 23.88, 30.82, 36.35, 21.82, 150.61 (2021, Winter Storm Uri), 62.93, 48.69, 26.41, 32.66 (2025), and 34.02 for the nine months of 2026.
- **Market energy, a flat load, last twelve months:** the span's flat price; USD = sum of `flat` x MW.
- **Market energy, this load; what the flexibility saves; this load, if perfectly foreseen** (a load that is not flat): section 5. "The rule kept p percent of it" = 100 x the rule's saving / the foreseen saving, rounded to a whole percent.
- **The hub beside it** (ERCOT's load zones only). The region's `ref` in the index: North, Houston, South and West each stand beside the hub of the same name; the four municipal and cooperative zones beside the hub average. A flat load at that hub over the zone's own twelve months, when all twelve count there; and "the load zone is d per MWh above (or below) its hub", d = the absolute difference of the two flat prices. Default: `HB_NORTH` 284,754.13 / 8,760 = 32.51; 33.73 - 32.51 = 1.22 above. No figure of the load is computed from the hub.
- **A bad month** and **power per GPU-hour:** 4.4 and 4.5.
- **Delivery and transmission, Texas** (never added to the market cost). **Session 236:** the four utilities' charges left the cost table for a table of their own under it, one row a component in USD per MWh with the total (4.18); the tariff's own lines (`texas_delivery_charges`, 41 rows of four utilities) are in the download. Until then each charge was printed in the cost table as its tariff prints it, and two figures were computed, of which the second stays a row of the cost table:
  - **The transmission factor alone, a flat load** = factor (USD per kW of four-coincident-peak demand a month) x 12 x 1,000 / 8,760, USD per MWh. A flat load's demand in those four intervals is its size. Until session 236 computed only where the factor is printed per kW: Oncor 6.260839 gives 8.58; AEP Texas 5.956038 gives 8.16. Both figures are now the transmission component of 4.18, unchanged; CenterPoint's and Texas-New Mexico Power's, printed per kVA, are converted there at a power factor of 1.
  - **Wholesale transmission, all of ERCOT** = the Commission's statewide rate (USD per kW of four-peak demand a year) x 1,000 / 8,760: 68.547301 gives 7.83 (2025, approved); 75.527270 gives 8.62 (2026, filed, not approved).
  - Both divide by 8,760 in a leap year too.
- **Other grids:** "Delivery charges: not held yet".

### 4.7 Will the power be there

- **Demand growth; the highest hour of demand; installed capacity by fuel:** the demand tool's and the mix tool's own files (`eia930_demand_growth`, `grid_stress_yearly`), newest whole year. Not computed here.
- **Hours the grid was tight** (the builder; `TIGHT` 0.95). From the operator's own hourly demand (`ercot_zone_load_hourly`, entity `ercot:system`; `caiso_area_load_hourly`, `caiso:system`; `nyiso_zone_load_hourly`, the sum of its eleven zones in the hours all eleven are held), placed on standard time. For a year with at least 95 percent of its hours of demand held: peak = the year's highest hour; an hour is tight when demand >= 0.95 x peak. The newest year is counted up to its last hour held and is marked not whole. The row shows the newest whole year. Default: 2025, peak 83,679 MW, 140 tight hours. "In Feb, Jul, Aug, Sep, between 07:00 and 19:00" lists the months that hold a tight hour and the earliest and latest hour of the day any of them falls in: an envelope, not a statement that every hour between is tight.
- **Of those hours, this load was off in** = the count of the year's tight hours in which the region's price is held and the load's weight is 0, under the rule. A flat load: none. A shifting load is not counted.
- **Demand by region:** each zone's mean hourly demand in its newest whole year against its first whole year held (a year is whole with at least 95 percent of 8,760 or more hours).
- ISO-NE reads "licensed source needed" (its demand table is internal); SPP "not held yet".

### 4.8 How clean

- **The first four rows** are the mix tool's (`clean_energy_summary`), for the newest year whose twelve months that table holds. ERCOT today: 2024, because its 2025 holds eleven months there. So this block can stand on an older year than the tight hours above (2025); the table's head names the year.
- **This load's own hours** (`cleanShare`): over the hours of that year in which both the price and the grid's carbon-free share c (percent, one decimal; `clean_energy_hourly`, `carbon_free_share_pct`, entity `iso:<grid>`) are held: sum of c x w / sum of w; and a flat load's, sum of c / hours, over the same hours. Default: 43.61 percent over 8,784 hours of 2024. It is the share of the grid's generation that was carbon-free while the load ran, an average of the hour, not the marginal plant and not a claim about the energy bought.

### 4.9 How soon

Figures of the queue tool (`interconnection_queue_summary`), of ERCOT's large load status (`ercot_large_load_status`) and the two blocks "How long a large load waits" and "Rules in motion", each from its own file of aggregates. Their methods are in [`datacenter_cost.md`](datacenter_cost.md), "How soon"; nothing of them is computed from prices.

### 4.10 With your contract (computed in the browser, never sent)

**Session 213: this panel and section are gone.** The contract is two assumptions of a scenario (4.14, the battery page's form since session 208): a share of the energy and a price per MWh, both 0 by default, in the address with the other assumptions, read by the scenario's price, year's cost, GPU-hour, present value, all-in figure and sensitivity chart, and by the headline's first number. `LoadContract.tsx` stays on disk, undrawn. What follows is how the panel computed until then.

The reader types a share s of the energy (percent, held between 0 and 100) and a price c (USD per MWh). Over the load's last twelve months, with E = sum of `energy` x MW and K = sum of `cost` x MW (`contractResult`):

- contracted energy costs s x E x c; the rest pays the market, (1 - s) x K; the total is their sum, and per MWh the total / E;
- without the contract: K, and K / E;
- a bad month with the contract: s x c + (1 - s) x the bad month's price per MWh.

Default with 50 percent at USD 30: 0.5 x 876,000 x 30 = 13,140,000; 0.5 x 29,546,505 = 14,773,252.50; together USD 27,913,252.50, or 31.86 per MWh against 33.73. Not in it: shape, settlement point, collateral, term.

### 4.11 The folds

- **Every year, every month:** the figures of 4.6 and 4.1 for each year and month held, the incomplete ones muted, with the hours off and the months or hours held.
- **Every region of the grid, a flat load:** each region's own last twelve months in the market chosen, with the months they are. Regions of one grid can stand on different months (section 6, item 5).
- **The Commission's transmission charge matrix:** as printed.

### 4.15 Will the power be there? (session 228)

The page's second question, answered for the load the reader describes, between "What will it pay?" and "How clean?". Computed by `site/lib/datacenter/answers.ts` (`scarcity`) from the page's own price files, for the last twelve months of 4.1; recomputed by `scripts/check-values.mjs` from the same files (check keys `dc|<address>|scarce:...`, the address being the inputs in force and the size).

- **The scarcity level.** An hour is counted short when the region's hourly price, in the market bought in, is at or above USD 1,000 per MWh (`SCARCITY_USD`): the cap on an incremental energy offer in every FERC market (Order 831, 2016; CAISO's soft cap, NYISO's, ISO-NE's and SPP's); in ERCOT, outside FERC, a price above it comes from its scarcity pricing (the operating reserve demand curve adders) on top of offers. One level for every grid, so the count means the same thing everywhere. The operator's own emergency notices are counted beside it where a table holds them: CAISO's (`caiso_grid_emergencies`, the notices dated in the twelve months; the table runs to 30 April 2025); no other grid's notices are held as a table, and the page says so.
- **The ruling, and each grid's own signal (session 236).** The owner's ruling of 12 October 2026 (the review of that day, section F): USD 1,000 per MWh stays the level for every grid, and it is stated on the page where the count stands (the first row of the table "The two counts", `LEVEL_WORDS` in `LoadAnswers.tsx`); each grid's own signal is a second count where the warehouse holds a table of it, the next rows of that table. The words beside the count: the level is the cap on an incremental energy offer in the FERC markets (Order 831); ERCOT is outside FERC and its own cap is higher (USD 5,000, as the review states it), and the same level is used there so that the count means the same thing on every grid. They do not repeat the sentence above that in ERCOT a price over the level comes from the adders: with a cap of USD 5,000 an offer can also be above USD 1,000, so that sentence is left for the owner's ruling (the session's report).
  - **CAISO: its notices** (`caiso_grid_emergencies`, events: flex alerts, restricted maintenance operations, transmission and energy emergencies, as CAISO posted them). Two counts, each with its check key: the notices dated in the page's twelve months (`dc|<address>|notices:count`), and, because the table ends on 30 April 2025, the notices dated in the last twelve calendar months the table itself covers (`notices:own:count`: the twelve months ending with the month of its newest notice, `elevenBefore` in `answers.ts`), with those months named and the line "Not the months of the price count above". When the first count is 0 and the table ends before the twelve months began, the page says it is not a count of none.
  - **ERCOT: its reserve adder** (session 236, after the hand-back; the table `ercot_rtm_price_adders` landed with session 244 at about 07:05 UTC on 13 October 2026, [`ercot_rt_price_adders.md`](ercot_rt_price_adders.md)). ERCOT's own scarcity signal is the adder of its operating reserve demand curve: the price it added to real-time energy when its reserves ran short. The count: the hours in which the on-line adder's hourly mean (`rtorpa_mean`, entity `ercot:system`, USD per MWh) was at or above USD 100 (`ADDER_USD` in `answers.ts`). A bare "above zero" would mislead: it is mostly fractions of a cent (session 244's report).
    - **What it covers, and where it ends.** ERCOT published the adder from 1 June 2014 to 4 December 2025 and no longer: since 5 December 2025 it prices scarcity through its real-time ancillary services, a report the warehouse does not hold. So the count over the page's twelve months covers only the hours of them the table holds, and the page says so beside it with the number of those hours and their first and last day (in the grid's standard time). Default case (October 2025 to September 2026): 1,558 hours, 1 October to 4 December 2025, of which 0 at or above USD 100. Check keys `dc|<address>|adders:hours` and `adders:held`.
    - **The year to its last hour.** Beside it, as for CAISO's notices: the same count over the 8,760 hours ending with the adder's last hour held (`adders:own:hours`), with its days named and the line "Not the months of the price count above". Default case: 5 December 2024 to 4 December 2025, 1 hour (the hour from 14:00 Central standard time on 30 June 2025, mean USD 412.74).
    - **Nothing is spliced.** From 5 December 2025 ERCOT's file carries only a reliability deployment adder (`rtrdpa`), which is another thing (it corrects the price for ERCOT's own out-of-market actions). It is not read, not counted and not joined to the ORDC adder; the page says so.
    - **The reads.** Two reads of the one variable, each bounded in time: the hours held since the first of the page's months, and the hours at or above the level since fourteen months before it. (A read of the whole variable is 100,878 rows, and an unbounded sort of it was cancelled by the database's statement timeout on 13 October, `runs/session236/probe3.out`.) The table is under `review_hold` (`warehouse/supabase/live_set.yaml`): loaded, read with the public key like every table a page in review reads, and left out of the counts a visitor sees. When the page's twelve months hold no hour of the adder (from December 2026 on), the row reads "not held" with the day the adder ended.
    - **At other levels**, for the ruling: over the same 1,558 hours the hourly mean was at or above USD 1 in 8 hours and at or above USD 10 in 3.
    - **Session 228's sentence, tested.** The first bullet of this section says that in ERCOT a price above USD 1,000 comes from the operating reserve demand curve adders. The table does not bear that out for the page's months. The default case's four hours at or above USD 1,000 are all in January 2026, after the ORDC adder ended: no ORDC adder existed in them. The only adder the table holds for January 2026, the reliability deployment adder, had an hourly mean of USD 100 or more in one hour of the month (USD 156.99, from 07:00 Central standard time on 28 January; largest interval USD 319.01). So those prices were not made by an adder of this table. For the years the ORDC adder was published the sentence was not tested here (it needs the hourly prices set against the adder hour by hour); it stays flagged for those years, and the page does not repeat it.
  - **NYISO, ISO-NE, SPP:** their own signal is reserve shortage pricing; no table of those hours is held, and the row reads "not held".
- **The hours:** the count of hours of the twelve months with a price held at or above the level; **what a flat load paid in them:** the sum of their prices times MW; **when they fell:** by month, and the first and last clock hour in the grid's standard time (the hour index modulo 24).
- **The ways.** Three ways of running, the page's own (5.1, the rule decided before each hour): flat; flexible, the load's own way when "Your load" is flexible, else the form's default (off in 100 hours a year); shifting, the load's own when it shifts, else the form's default (20 percent). For each: the scarce hours its weight was 0 in (off), what a MW of it paid in the scarce hours (the sum of price x weight), and what it avoided against a flat MW (the flat sum less its own). Scenario A's way sets the headline's third number; scenario B's stands beside it where B runs the other way. A way that needs day-ahead prices the region does not hold is "not held".
- Default case (ERCOT, LZ_NORTH, real time, 100 MW, October 2025 to September 2026): 4 hours, all in January 2026 between 07:00 and 22:00 Central standard time; a flat load paid USD 446,175 in them; the flexible way (off in 100 hours) was off in 3 of them and avoided USD 306,942; the shifting way off in 3, USD 341,401. Rebuilt by the do-file and the Python mirror from `erw_2026_datacenter_hourly.csv` (section 8).

### 4.16 How clean? (session 228)

The third question. Computed by `answers.ts` (`l12Carbon`, `windowCarbon`, `yearlyCarbon`) from the ERW's carbon intensity of consumed electricity (`carbon_intensity_monthly` and `carbon_intensity_hourly`, variable `intensity_demand`, kg CO2 per MWh: generation plus imports less exports, from EIA-930's hourly CO2 estimates, `docs/methods/emissions.md`), for the grid's balancing authority (`eia930:ERCO`, `CISO`, `NYIS`, `ISNE`, `SWPP`), read from the live set; check keys `dc|<address>|co2:...`.

- **The last twelve months at the grid's monthly average.** For each way: the sum over the twelve months of the way's energy per MW (4.1, the sum of its weights) times the month's intensity, over the months of the twelve whose intensity the table holds (`months` of `of`), gives kg per MWh consumed; the tonnes a year apply that rate to the year's whole energy, times MW, over 1,000. Default case: 11 of the 12 months (the monthly table lacks one month of 2025), 303.14 kg per MWh, 265,548 tonnes a year for 100 MW.
- **The hours held hour by hour.** When session 228 wrote this the hourly table in the live set held its last 35 days (`warehouse/supabase/live_set.yaml`, the recent window); on 13 October 2026 it held 10,144 hours for ERCOT, 9 August 2025 to 9 October 2026 (session 236 saw it grow during its run), so the page names no length and prints the window's own first and last day. The default case's figures in this bullet are of the 35 days. Over the hours in which the region's price (so the way's weight) and the intensity are both held: each way's own-hours intensity is the sum of weight x intensity over the sum of weights; the grid's mean over the same hours stands beside it. The hour's intensity is matched to the page's hour by its UTC start (`hourUtcMs`: the year file's hour index plus the grid's standard-time offset). Default case: 776 hours, 7 September to 9 October 2026; flat and flexible 346.71 (the flexible way was off in none of them), shifting 334.82, the grid 346.71.
- **By year:** the mean of the months held of each calendar year, with the count (`years`). Default case: 2019 414.04 to 2025 314.26.
- Rebuilt by the do-file and the Python mirror from `erw_2026_datacenter_carbon.csv` beside the hourly file (section 8): the monthly intensity, every month held, and the hourly window, written from the live set by `site/scripts/write-datacenter-carbon.py`.

### 4.17 How soon? (session 228)

The fourth question, from public tables only (`ercot_large_load_status`; `large_load_rules` through the site's own file `data/datacenter/rules.json`). `large_load_statements` and `large_load_waits` are internal and are not read; `datacenter_queue_positions` is not in the live set and is flagged "license needed" for three of its operators, so it is not read either.

- **ERCOT:** `answers.ts` (`largeLoad`) reads every row of `ercot_large_load_status` (variables `approved_to_energize_mw`, `observed_nonsimultaneous_peak_mw`, `observed_simultaneous_peak_mw`, `new_submissions_count`, `new_submissions_mw`) into one report a day; the headline is the latest report with an approved figure, the change is measured from the newest report a year or more before it, or, while the reports span less than a year, from the earliest held (the page says which); the table is every report. Default case: 26 March 2026, 9,042 MW approved, 4,004 MW observed running at the non-simultaneous peak (3,522 simultaneous), up 2,168 MW since the earliest report held (28 May 2025); 137 new submissions totalling 140,000 MW by 13 March 2026. Check keys `dc|<address>|ll:report:<day>:<field>` and `ll:approved_change`.
- **Every other grid:** one line, "<grid> publishes no figure of large load waiting or energized that the warehouse holds as a public table, so none is stated here, and no wait is estimated."
- **The rules a large load must meet:** the count of proceedings and orders in motion for the grid in the public dockets held (`lib/rules.ts`, as the block "Rules in motion" counted them until session 213), with the newest named; the rows are in the download. No wait time is estimated anywhere: none is published.

### 4.18 Delivery charges in Texas, by component (session 236)

The owner's chain prompt of 12 October 2026: "one row per component with its USD per MWh and the total; the tariff lines go to the CSV". Computed by `site/lib/datacenter/delivery.ts` from the site's own file `data/datacenter/texas_delivery.json` (the table `texas_delivery_charges`, 41 tariff lines of Oncor, CenterPoint Energy Houston Electric, AEP Texas and Texas-New Mexico Power, each for service at transmission voltage); recomputed by `scripts/check-values.mjs` from the same file (check keys `dcd|<MW>|<utility>:<transmission, distribution, other or total>`). Shown for ERCOT only, under the cost table, a column a utility; never added to the market cost.

- **A line in USD per MWh, for a flat load of the reader's size** (`perMwh`), by the unit its tariff prints (`basisOf`):
  - a rate per kW or per kVA a month, whether on the four coincident peaks or on billing demand: rate x 12 x 1,000 / 8,760. A flat load's demand in the four peak intervals and its billing demand are its size; a kVA is counted as a kW (a power factor of 1); the year is 8,760 hours, in a leap year too;
  - a rate per kWh: rate x 1,000;
  - a rate per retail customer, per meter or per ESI ID a month: rate x 12 / (MW x 8,760), one account with one meter. This is the only part that depends on the size typed.
  - a unit that names none of these is not converted and is counted as left out (none today).
- **A component** (`deliveryOf`) is the sum of a utility's lines of one kind, as the file classes them: transmission (the transmission cost recovery factor and the transmission system charge), distribution (metering, customer, distribution system and distribution cost recovery charges), other riders (surcharges, credits, nuclear decommissioning). **Lines that apply only to some loads by the tariff's own words** (`applies` beginning "conditional": CenterPoint's municipal account franchise credit, Texas-New Mexico Power's municipal franchise fees, AEP Texas's nuclear decommissioning rider of one former service area) are not added; the note under the table gives their count (3) and they stand in the download with the reason.
- **The total** is the sum of the three components. Each figure is rounded to the cent (`deliveryStat`), so a total can differ by a cent from the sum of the three figures shown.
- Default case (100 MW): Oncor's transmission 6.260839 x 12,000 / 8,760 = 8.58 and AEP Texas's 5.956038 x 12,000 / 8,760 = 8.16, the two figures the page stated until this session, unchanged. The other figures are new: the page stated no distribution figure, no figure of the other riders and no total before.
- **The tariff's own lines** are the table `delivery` of `tables.csv`: for each line the schedule's name, its component, the rate as filed and its unit, what it comes to in USD per MWh with the rule used (blank with the reason for a conditional line), its document, page, date and address, and the line it was read from; then each utility's sums and total with their check keys. The page shows no schedule name and no rate as filed.
- **The Commission's wholesale rate** (4.6) stays a row of the cost table, in USD per MWh; the rate per kW as printed is on hover and in the download's table `matrix`.

### 4.19 Scenario B at a site of its own (session 236)

The owner's chain prompt of 12 October 2026: scenarios A and B "compare two sites or two contracts". Two contracts were already two assumptions of each scenario (the share of the energy and its price, 4.14). For two sites, the address may carry `bsite=<grid>:<region>` (`SITE_B` in `finance.ts`; chosen in the block, `LoadSiteB.tsx`; carried by "Your load" like the scenarios' own parameters). It is read by the server (`siteBOf` in `app/cost-of-power/model.ts`): a grid or region the files do not hold, or A's own site, leaves B at A's site, and the block says so.

- **B's two ways of running** are computed exactly as A's (4.14, "the two ways"), with the same market, the same way "Your load" runs and the same rule, from that site's own price files over that site's own last twelve months (which can be other months than A's: the row "What differs" then names them). B's column, the row "B against A" and B's sensitivity chart read them; A's column, the headline and every figure above are untouched.
- **The three answers** each add B's site: its hours at or above USD 1,000 and what a flat load paid in them, its carbon at its grid's monthly average for the way B runs, and its grid's large load figure or the line that none is held. They are `readAnswers` for that site's address, so their check keys name that site (`dc|grid=<B's grid>&region=<B's region>&...`).
- **The download** `tables.csv` then holds the table `scenario_b_site`.
- With no `bsite` nothing is computed for B's site and every figure is what it was.

### 4.12 The source line

The tables the index names, the day the price files were built, the two stated defaults with their sources on hover, and the three downloads of section 8.

### 4.13 The view "Grid by grid"

`/cost-of-power?view=grids` is what the tab showed before session 138: the ranking by ISO, ERCOT since 2018, the hours of the day, cost against carbon and a calculator, from the `cost_of_power_*` tables. Its method is [`cost_of_power.md`](cost_of_power.md); `check-values.mjs` checks its 83 values against the live set. It shares no number with the view above: it reads other tables, weighs by the grid's load and uses each grid's main trading hub.

### 4.14 Scenarios A and B (session 194)

On the page this block stands after "With your contract" (4.10) and before "Will the power be there" (4.7). It is computed in the browser by `site/lib/datacenter/finance.ts` from figures the server already computed for the page; a change sends no request and rewrites the address in place (`history.replaceState`). It adds no number to the page above it and changes none. Worked figures are the default case as the files stood on 11 October 2026.

**Session 195: the block is the one the three decision pages share**, described once in `battery_earns_algorithm.md`, section 11.1, "The block the three pages share": the panel, the two columns, the rows in words, the chart, where the scenarios are held, the old names, and that nothing is sent. On this page scenario A sets the three headline numbers (4.3 to 4.5); the power per GPU and the overhead ratio are scenario A's and no longer fields of "Your load", so their defaults are the two the page cites, 1.3 kW and 1.56, whatever an older link held; the sentence under the table states scenario A, whichever scenario is in view. Default case, before and after: 33.73 USD per MWh, 37.88 in a bad month, USD 0.0684 per GPU-hour. No number moved. Checks: `site/scripts/check-decisions-face.mjs`; `site/scripts/check-datacenter-scenarios.mjs`, part 8b; `tests/test_session195.py`.

**What a scenario reads from the page.** Two ways of running the same load over the same last twelve months (4.1), per MW:

- *flat*: `per` = sum of prices / hours held, `cost` = sum of prices, `energy` = hours held. Default: 33.7289, USD 295,465.05, 8,760 MWh.
- *flexible*: the load under the rule of section 5.1, its own `cost`, `energy` and hours off. When "Your load" is flexible it is that load. When "Your load" is flat it is a load off in 100 hours of each calendar year (the form's default), computed by the same rule. Default: 31.4583, USD 272,428.84, 8,660 MWh, off in 100 hours. Not held where the region has no day-ahead price (the rule cannot decide).
- each way's bad month (4.4), over its own 36 months. Flat: August 2026, 37.88. Flexible: August 2024, 35.43.
- The way "Your load" describes is the page's own figure; the other is one more pass of the same functions (`monthsRuled`, `lastTwelve`, `span`, `badMonth`). A flat load over a flexible load's months is each month's `flat` and `held`, which is what `monthsOf` gives a flat load.

**The eight assumptions.** Each has a Reset; "Reset all" returns a scenario to the defaults; "Copy A to B" makes B equal to A.

**Session 213: ten.** The contract's share of the energy (`an`, `bn`; percent, 0 to 100, chart step 10 points) and its price (`ac`, `bc`; USD per MWh, 0 to 1,000, step USD 1) are the ninth and tenth, both 0 by default (no contract: fully merchant). The contracted share s of the energy is bought at the contract price c in every year counted and pays nothing to the market; the rest pays the market, changing by the yearly rate. With `K` the market's cost of the last twelve months and `E` their energy, per MW: the market's cost a year is `(1 - s) x K`, the contract's `s x E x c`; the price is `((1 - s) x K + s x E x c) / E + adder`; the year's cost `(1 - s) x K + s x E x c + adder x E`; the cost of year t `((1 - s) x K + adder x E) x (1 + g)^(t - 1) + s x E x c` (the market's cost and the other charges change by the rate, as before; the contract's price is fixed); the present value, the GPU-hour and the all-in figure follow from these as 4.14 says. The fixed price with the same present value does not read the contract: it is the market's breakeven for the whole of the energy. The sensitivity chart draws the two contract rows only when the scenario holds a contract. At s = 0 every expression is the old one in the old order, to the bit (`site/scripts/test-datacenter-finance.mjs`, the session 213 block; `tests/test_session194.py`, the Python mirror on the same cases).

| Assumption | Address | Default | Source of the default | Bounds | Chart step |
|---|---|---|---|---|---|
| How the load runs | `aw`, `bw` (0 flat, 1 flexible) | as "Your load" | the reader's own input | the ways held | the other way |
| Power per GPU, kW | `ag`, `bg` | 1.3 (until session 195: as "Your load") | NVIDIA DGX H100 datasheet (section 7) | 0.05 to 20 | 0.1 |
| Facility overhead ratio | `ap`, `bp` | 1.56 (until session 195: as "Your load") | Uptime Institute, Global Data Center Survey 2024 (section 7) | 1 to 3 | 0.1 |
| Delivery and other charges, USD per MWh | `ad`, `bd` | 0 | the page's figure is market energy alone | 0 to 500 | 5 |
| Change of prices, percent a year | `ae`, `be` | 0 | **none held**: the last twelve months are repeated | -20 to 20 | 1 point |
| Upfront cost, USD per kW of the load's size | `au`, `bu` | 0 | **none held** | 0 to 20,000 | 100 |
| Years counted | `al`, `bl` | 20 | **none held** | 1 to 40, whole | 5 |
| Hurdle rate, percent a year | `ah`, `bh` | 9.6 | Lazard, Levelized Cost of Energy+, June 2025: "60% debt at an 8% interest rate and 40% equity at a 12% cost"; the default is that weighted cost, 0.6 x 8 + 0.4 x 12 (session 196; until then 8). It is a power plant builder's cost of capital: none is cited for a datacenter's own | 0 to 40 | 1 point |

`v=b` puts B in view. Only what differs from the defaults is written, so the bare address is the defaults. The three defaults marked "none held" are to be confirmed by the owner (the hurdle rate was the fourth until session 196); the page says "No cited ..." beside each.

**The formulas.** For a scenario with way w (`per`, `cost`, `energy`, `held`, `flatCost`, `down`), per MW; the page multiplies by the megawatts. Rates are fractions here: g the change of prices, r the hurdle rate, N the years counted, U the upfront cost per kW, d the other charges.

- price = cost / energy + d. Row 1 shows cost / energy alone (market energy).
- bill = cost + d x energy. Default: USD 295,465.05 a MW, USD 29,546,505 for 100 MW, the page's first headline.
- per GPU-hour = price x kW per GPU x overhead ratio / 1,000 (4.5). GPUs a MW = 1,000 / (kW per GPU x overhead ratio). GPU-hours a year a MW = energy x GPUs a MW. Default: 0.0684; 49,310 GPUs and 431,952,663 GPU-hours for 100 MW.
- hours off = `down`; energy not bought = held - energy; **breakeven value of a GPU-hour** = ((flatCost - cost) / (held - energy) + d) x kW per GPU x overhead ratio / 1,000. `flatCost` is what a flat MW paid over the same hours, so flatCost - cost is what the hours off would have cost. Default flexible way: (295,465.05 - 272,428.84) / 100 = USD 230.36 per MWh not bought, USD 0.4672 per GPU-hour not run. An hour off saves more than it gives up when a GPU-hour earns less than that. "none" for a flat load and for a load that shifts within the day.
- C_0 = 1,000 x U; C_t = bill x (1 + g)^(t - 1) for t = 1 to N. All costs, all positive.
- **present value of the cost** = sum over t = 0 to N of C_t / (1 + r)^t. Default: 295,465.05 x 8.751270 = USD 2,585,694 a MW, USD 258.57 million for 100 MW. 8.751270 = sum of 1 / 1.096^t over 20 years. (Until session 196, at 8 percent: 9.818147 and USD 290.09 million.)
- **fixed price with the same present value** = (cost / energy) x [sum of (1 + g)^(t - 1) / (1 + r)^t] / [sum of 1 / (1 + r)^t], both sums over t = 1 to N. Market energy only: the other charges and the upfront cost are paid either way. With g = 0 it is the last twelve months' price, 33.73. With prices rising 2 percent a year it is 38.66 (39.00 at 8 percent).
- **all-in power per GPU-hour** = present value of the cost / (GPU-hours a year x sum of 1 / (1 + r)^t). With U = 0 and g = 0 it is the page's power per GPU-hour.

**B against A.** With pv_A, pv_B the two present values:

- the year's cost: bill_B - bill_A; the GPU-hours a year: B's less A's; the present value: pv_B - pv_A, each scenario over its own years and at its own hurdle rate.
- **the upfront cost of B at which the two present values are equal** = (pv_A - (pv_B - 1,000 x U_B)) / 1,000, USD per kW. Below zero: no upfront cost of B does, and the row says so.
- **the rate the dearer upfront cost returns**, when one scenario costs more upfront and both count the same years: the rate that sets -1,000 x (U_more - U_other) + sum of (C_t of the other - C_t of the dearer) / (1 + rate)^t to zero, by bisection between -99 and 1,000 percent (the code of the generator page, section 11.3 of `generator_earns_algorithm.md`). The row states it beside that scenario's hurdle rate. Not stated when the two count different years; "no rate" when none in the bracket does.
- Example, A the default and B flexible with USD 50 per kW upfront: B's year is USD 2.3 million lower (27.24 against 29.55 million); B runs 4,930,966 fewer GPU-hours a year; B's present value is USD 15.16 million lower over 20 years at 9.6 percent; the two are equal when B's upfront cost is USD 201.60 per kW; B's USD 50 per kW returns 46.0 percent a year.

**The chart.** For the scenario in view, each assumption moved by its step down and up with the others held, and the all-in power per GPU-hour recomputed: two thin bars from the scenario's own figure, largest move first. The way of running has one step, the other way. A step that leaves the bounds is not drawn. Pointing at a row, or tabbing to it, states the two values; "The chart as a table" holds the same figures. A move smaller than one part in 10^12 of the figure counts as none: at the defaults the years counted and the hurdle rate move nothing, because the same rate discounts the cost and the GPU-hours.

**What this block is not.**

- Not a forecast: the last twelve months are repeated, changed only by the rate the reader types.
- Not a value of compute. A scenario that runs fewer hours has a lower year's cost; what the GPU-hours not run would have earned is the reader's own figure, and the breakeven row is what to set it against.
- A lower overhead ratio changes how many GPUs a MW powers, not the energy a MW buys: it moves the GPU-hour rows and no bill, so no rate of return is stated for it.
- The contract typed in "Your contract" is not read: its terms stay on the device (4.10) and a shared link could not carry them.
- The foreseen load (5.2) is not used. Finding 1 of section 11 (a year held in part gives the rule 100 hours and the foreseen load fewer) therefore moves no figure of this block; it stands as it was, for the owner's ruling.
- Finding 2 of section 11 holds here as on the page: for New York bought in real time both ways stand on July 2025 to June 2026, and every row of the block says which months it is.
- No usage count is sent from the block, as on the battery and generator pages: the owner's ruling of 11 October 2026 (session 195) closes the question.

**Checks.** `site/scripts/test-datacenter-finance.mjs` (hand cases; the generator page's library on 300 seeded cases; every grid's main region against the page's own figures). `tests/test_session194.py` (a Python mirror of every formula above, to 1e-6 on seeded cases; the page's source). `site/scripts/check-datacenter-scenarios.mjs` (the block in a browser at 1280 and 390 px).

## 5. A load that is not flat

It is computed twice. The page's figure is a rule an operator could follow. Beside it stands the same load "if perfectly foreseen".

### 5.1 The rule (`ruleWeights`, `ruleThresholds`)

Every decision for an hour reads only prices published before the hour: the day-ahead prices. What the load pays is the price of the market it buys in.

**Off in n hours a year, or in a share of hours.**

1. q = the share of hours to shed: n / 8,760, or pct / 100 (at most 1).
2. For each day d of standard time: take the 720 hours before the day's first hour (the prior 30 days), across the boundary of two years. H = the number of them with a day-ahead price. If the day is among the first 30 days of the first year held, or H < 0.95 x 720 = 684, the day is not decided: the load runs.
3. k = round(q x H), at least 1 and at most H. For n = 100 and H = 720: round(8.22) = 8. For 5 percent: 36.
4. The threshold T of the day = the k-th dearest of those H day-ahead prices.
5. The hours of day d whose day-ahead price is at or above T, and whose price in the market bought is held, are candidates, dearest day-ahead price first (ties by the earlier hour).
6. **The budget.** Each calendar year the load may be off in B = round(q x the year's hours) hours: 100 for n = 100; 438 for 5 percent (439 in a leap year). The candidates are taken while the year's budget lasts. Once it is used the load runs for the rest of that year.

**Shifting** (shift percent of each day's energy). h = 24 x shift / 100 hours (4.8 for 20 percent). In each day whose 24 day-ahead prices and 24 prices of the market bought are all held: the weight falls by 1 in the floor(h) dearest day-ahead hours and rises by 1 in the same number of cheapest ones; the next dearest and next cheapest move the fraction left (0.8). The day's energy is unchanged; an hour's weight is between 0 and 2. A day with an hour missing is not shifted.

A region with no day-ahead price gives no figure under the rule: the placeholder says so.

### 5.2 If perfectly foreseen (`weights`)

The same load with its hours chosen knowing every price of the market it buys in:

- **Off in n hours:** in each calendar year, the K dearest hours held, K = round(n x hours held / hours of the year). A whole year: n.
- **Off in a share:** the dearest round(pct / 100 x hours held) of each year.
- **Shifting:** as the rule, but ranked by the price paid and needing only that price.

### 5.3 Worked example: off in 100 hours a year, `LZ_NORTH`, real time

- **The year's budget.** In 2025 the rule was off in 29 hours of January, 21 of February, 5, 7, 13, 4, 16 and 5 in March to August: 100 by August, none after. In 2026: 55 hours in January, 24 in March, 14 in April, 1, 3 and 3 in May to July; the hundredth on 5 July. In August and September 2026, the fourth and second dearest months of the last 36, the load ran every hour.
- **One day by hand, 20 January 2026**, the first day of 2026 the load was off. The 720 prior hours all hold a day-ahead price; k = 8; the eight dearest are 86.78, 81.90, 72.95, 70.37, 68.42, 61.48, 60.50 and **59.60**: T = 59.60. Three hours of the day stand at or above it: 05:00, 06:00 and 07:00 (day-ahead 65.76, 80.61 and 81.74). The next dearest hour of the day is 53.12. The load is off in those three hours, whose real-time prices were 70.55, 73.90 and 136.80.
- **The last twelve months** hold 100 hours off, all of 2026 (none of October to December 2025): cost 272,428.84 over 8,660 MWh = **31.46** per MWh, against 33.73 flat: 2.27 less.
- **Foreseen:** 109 hours off in the same twelve months (the part of 2025's 100 that falls in October to December, and of 2026's 76): **29.72**, 4.01 less. "The rule kept 57 percent of it."
- Bought day-ahead: 30.99 against 35.33 flat; foreseen 30.54. Shifting 20 percent, real time: 24.80, foreseen 22.88; bought day-ahead: 25.87 both, since the rule ranks by the prices it pays.

## 6. Edge cases, as the code handles them

1. **A missing 15-minute price.** The hour has no price and is in no figure. It lowers the month's hours; under 95 percent the month does not count. The default case holds every one of its 103,055 hours.
2. **A month enters the last twelve months before it ends.** A month counts at 95 percent of its hours: a 31-day month from the 707th hour, in its 30th day. The headline then moves to a window whose last month lacks its last hours. For the default region this cannot happen today: its hours stop on 3 October 2026 (item 4). Section 10, item 6.
3. **One missing month blocks every later window.** The last twelve months must be twelve counted months in a row. New York's real-time prices lack 19 days of July 2026, so July 2026 does not count and New York's real-time "last twelve months" are July 2025 to June 2026 for every zone. They will stay there until July 2027 is held (the first twelve months in a row after the gap are August 2026 to July 2027) unless those days are filled. Day-ahead is whole: October 2025 to September 2026. With no market named, New York City opens in real time, on the older window (USD 68.49); day-ahead reads 73.10. Each figure says its months. Section 10, item 9.
4. **ERCOT's load zones stop on 3 October 2026.** `ercot_zone_prices_history` is refreshed only by the data machine's run, which is registered nowhere; the runner holds no load zone price. The hubs go on (to 10 October). So the default page's last twelve months will stay October 2025 to September 2026 while the hubs' move on. Section 10, item 4.
5. **Regions of one grid on different months.** Each region's last twelve months are its own. The fold "Every region" prints each one's months.
6. **Paused and licensed markets.** MISO and PJM cannot be chosen; an address that names one shows ERCOT's prices under ERCOT's name, and the two blocks that follow the grid named. MISO's eight hub names are in the index (names only, no number).
7. **Daylight saving.** There is none on this page: section 3. The operator's files are in prevailing time; the tables hold UTC; the builder subtracts the standard offset. The repeated hour of November and the missing hour of March do not exist in UTC, and every one of the default case's hours holds four 15-minute rows.
8. **A partial month** is in the folds (muted) and in no figure. October 2026 holds 71 of 744 hours for the default region.
9. **A year held in part** is hatched in the chart and holds its counted months only: 2026 is January to September.
10. **A leap year** has 8,784 hours; the share to shed is still n / 8,760; the transmission figures still divide by 8,760.
11. **A year held in part, for a flexible load: the rule and the foreseen load get different hours.** The rule's budget is the whole year's (100 hours for 2026, although 2026 is held to 3 October); the foreseen load's is pro-rated (76). In a year held in part the foreseen figure is therefore not the most the rule's load could have saved. New York City, real time, 100 hours, the year 2026 on the chart and in the fold: the rule 63.93 against "if perfectly foreseen" 63.97. Section 11, finding 1.
12. **The rule spends its hours early.** Example 5.3: none left for August and September 2026. By the owner's ruling of 7 October 2026 the budget stays.
13. **The last twelve months of a load that turns off hold parts of two years' budgets**, so the hours off in them need not be n (the default example: 100 under the rule, 109 foreseen; at 5 percent, 470 and 448).
14. **A day not decided.** The first 30 days a region is held, and a day whose prior 720 hours hold fewer than 684 day-ahead prices: the load runs. For `LZ_NORTH`: 1 to 30 January 2015, and the days after 5 October 2026.
15. **A negative price** is a price: a flat load is paid in that hour, and the sums take it as it is.
16. **A load that turns off pays per MWh consumed**, so its price can fall while its bill falls more; the row "what the flexibility saves" gives both, and the MWh not bought.
17. **Rounding to the cent.** An hour's real-time price is the mean of four prices rounded to the cent. Over the default case's 103,055 hours the mean of the rounded hours is 43.000916 and of the unrounded 43.000952: a difference of 0.00004 USD per MWh.
18. **A value changed after it was built.** A new build's hour replaces the kept hour, so a corrected price reaches the page at the next build. The Saturday build of 10 October 2026 on the runner added 2,376 hours to the five grids' 2026 files, removed none and changed none (`runs/session190/saturday_run.out`).
19. **The hub beside the zone** needs all twelve of the zone's months to count at the hub; otherwise its cell is a placeholder.
20. **The files cannot be read.** One line says so and no cost figure is shown; the other three sections still show.

## 7. Assumptions, their defaults and sources

| Assumption | Default | Source |
|---|---|---|
| Power per GPU | 1.3 kW | NVIDIA DGX H100 system: 8 H100 GPUs, maximum system power 10.2 kW (10.2 / 8 = 1.275, stated as about 1.3). The reader can change it |
| Facility overhead ratio | 1.56 | Uptime Institute, Global Data Center Survey 2024, the industry average. The reader can change it |
| A month counts | 95 percent of its hours | the ERW's rule (`NEAR`); the comparison page uses the same. No outside source |
| A bad month | the top tenth of the last 36 months, nearest rank | the ERW's choice, the mirror of the battery page's 10th-percentile month. No outside source |
| Tight | demand at or above 95 percent of the year's highest hour | the ERW's choice (`TIGHT`). No outside source. A count of high demand, not of scarcity |
| The rule's memory | the prior 30 days of day-ahead prices | the ERW's choice (`PRIOR_DAYS`). No outside source |
| The rule's budget | the hours named, each calendar year | session 140; the owner's ruling of 7 October 2026 |
| A load turns off whole, at once, with no minimum | by construction | no source; a real load has a minimum and takes time to stop and start |
| A flat load's four-peak demand is its size | by construction | for the two transmission figures of 4.6 |
| Wholesale energy only | by construction | no delivery, ancillary, uplift or capacity charge, no retail margin, no tax |
| A hub or zone is not a site | by construction | the price at one substation differs by congestion and losses |
| Scenarios: other charges, change of prices, upfront cost (session 194) | 0, 0, 0 | no source: the page's own figure with nothing added (4.14) |
| Scenarios: years counted (session 194) | 20 | no cited term is held; to be confirmed by the owner (4.14) |
| Scenarios: cost of capital (session 194; the default since session 196) | 9.6 percent | Lazard, *Levelized Cost of Energy+*, June 2025: "60% debt at an 8% interest rate and 40% equity at a 12% cost", the weighted cost 0.6 x 8 + 0.4 x 12; the owner's ruling of 11 October 2026 (session 196), labelled "a generator's WACC, Lazard" since session 265. Session 194 set 8 percent; this row said so until session 462 |

## 8. The replication

**The files** (`site/public/datacenter/`, linked from the page's source line):

- `erw_2026_datacenter_hourly.csv`: the default case hour by hour. 103,055 hours from 1 January 2015 to 3 October 2026, 142 months, 5.0 MB, 15 provenance lines. Columns: `hour_utc`, `std_month` (the hour's month in Central standard time), `rt_usd_mwh` (`LZ_NORTH`, real time), `da_usd_mwh` (`LZ_NORTH`, day-ahead), `hub_rt_usd_mwh` (`HB_NORTH`, real time), `in_last_twelve`. `-99999` in a price column marks an hour not held; today no hour of the file is.
- `erw_2026_datacenter_replication.do`: the Stata do-file, to your rules (no line continuation; one empty line between commands outside loops and none inside; every numeric variable destrung with force; the sentinel recoded variable by variable before any loop or collapse; real numbers as doubles). **It has never been run: Stata is not on this machine.**
- `erw_2026_datacenter_replication.py`: its Python mirror, standard library only, step for step, printing the same 30 lines.

**The exporter** (`warehouse/derived/datacenter_hourly_export.py`) reads the page's own files, so it runs on any machine and needs no table. It refuses to write unless the rows, as written, give back every hour of the files and every month the page computes. With `--tables` it also sets every hour against the price tables (section 3).

**What the do-file rebuilds, and what the page shows:**

| Number | Page | From the CSV |
|---|---|---|
| Last twelve months; months that count; hours | Oct 2025 to Sep 2026; 12; 8,760 | the same |
| Market energy, USD per MWh | 33.73 | 33.73 |
| Cost and energy for 100 MW | USD 29.55 million; 876,000 MWh | 29,546,505; 876,000 |
| Power per GPU-hour; GPUs | 0.0684; 49,310 | the same |
| The hub beside it; the zone less its hub | 32.51; 1.22 above | 32.51; 1.22 |
| Bought day-ahead, the same twelve months (the page at `buy=da`) | 35.33 | 35.33 |
| By year, 2015 to 2026 | 24.04, 21.68, 23.88, 30.82, 36.35, 21.82, 150.61, 62.93, 48.69, 26.41, 32.66, 34.02 | the same |
| A bad month; its rank; the months it is taken over | 37.88, August 2026; of 36, October 2023 to September 2026 | 37.88, 2026-08; rank 4 of 36 |

The do-file and the page add the same cents in the same months, so they agree to the last decimal a double holds.

**Beyond the do-file, in the test** (`tests/test_session190_replication.py`): the flexible example of section 5.3 and seven others are rebuilt from the CSV's two price columns by a second implementation of the rule and of the foreseen load, written in Python from this note, and set beside the page's library run by node: the same hours off and the same price to 1e-9.

**Not in the do-file:** a flexible load, the contract, the delivery figures, the tight hours, the clean share and everything of "How soon".

**When the files go stale.** The CSV is written once. When the page's files gain or change an hour of the default case, `tests/test_session190_replication.py` fails on any machine, which is the alarm: run `python warehouse/derived/datacenter_hourly_export.py` (no table, no lock) and commit the CSV. The data machine's run does it after its own build of the page's files.

## 9. Where the notes and the code differ

1. `datacenter_cost.md` says the foreseen figure "is never worse than the rule's, and the two compare like for like". True of a whole year. Not of a year held in part (edge case 11).
2. `datacenter_cost.md` says SPP South holds "the days pulled so far". Since session 149 it holds day-ahead from 1 January 2019.
3. `datacenter_cost.md`, "Refresh", says ERCOT's load zones are not refreshed on a schedule "until a person rules on it". The owner ruled on 7 October 2026 and session 149 wrote the refresh into `run_data_machine.sh`; what is missing is that the run is registered nowhere.
4. The builder's `--in-dir` moves the price tables only. The demand, the carbon-free hours and the delivery charges are still read from the machine's own `warehouse/output`, so a trial build from another copy's tables keeps the kept files' tight hours and clean hours. No number is affected; the help text says "the price tables".
5. `lib/datacenter.ts` says at `weights` that "the hours are chosen knowing the year's prices: the most a load could have saved". See 1.
6. No note said the tight hours' "between 07:00 and 19:00" is an envelope (4.7).
7. No note said "How clean" can stand on an older year than the tight hours (4.8).
8. No note said one missing month holds New York's real-time window in place for a year (edge case 3).
9. The page's words and the code agree.

## 10. What is left, for your ruling

From this tool's reports (138, 140, 163) and from this session. Each with a recommendation. The session report has every item in the reports' own words.

| # | Item | From | State and recommendation |
|---|---|---|---|
| 1 | The Texas tariffs' terms; ISO-NE's demand; ISO-NE's zone prices; the budget of hours; NYISO's terms for the queue rows; how a flexible load's bound is said | 138, 140 | Closed: your rulings of 7 October 2026, applied in sessions 140 and 149 |
| 2 | Load zone prices; the zones' history; the Commission's matrix; the forecast rule; the load's own clean hours; New York's queue; SPP South's year | 138, 140 | Closed by sessions 140 and 149 |
| 3 | The first Saturday build on the runner | 138, 140 | Closed in this session: 2,376 hours added, none removed, none changed |
| 4 | ERCOT's load zones stop on 3 October 2026 | 140, 149 | Open. The refresh is written and never runs: `run_data_machine.sh` is registered nowhere. Recommend registering it; until then the default page's twelve months do not move |
| 5 | The tab on the battery page read "What power costs to buy" | 138, 140 | Closed in this session: the three tabs read alike. The menu and the home page still say "Cost of power": open; a visitor sees the menu, so it wants a landing of its own |
| 6 | A month enters the last twelve months at 95 percent | new | Open. Recommend whole months only for the headline, as recommended for the battery and the generator pages. Moves nothing today |
| 7 | The 2026 transmission matrices are filed, not approved | 140 | Open. Docket 59080 had no signed order on 7 October. A pull of the docket's list: your approval |
| 8 | Texas-New Mexico Power's transmission factor is probably superseded | 138, 140 | Open. A pull of its current tariff: your approval; its site refused the request once |
| 9 | New York's real-time prices lack 19 days of July 2026 | 140 | Open, and it now holds New York's real-time window in June 2026 until July 2027 is held (edge case 3). A NYISO pull, after your ruling on NYISO's terms; or show day-ahead first for New York until then |
| 10 | CAISO's ZP26 day-ahead begins 26 June 2023 | 140 | Closed as it stands: CAISO serves nothing earlier |
| 11 | The figure that rests on two requests ("How long a large load waits") | 163 | Open, yours. Recommend keeping it: the count and the group's two ends, no request's own range |
| 12 | Bonneville and Alberta are on none of the page's grids | 163 | Open. Recommend leaving them off: the page's grids are the seven organized markets, and both entities' terms wait for your word (session 165) |
| 13 | Stated waits held for CAISO, ISO-NE, SPP and PJM are not shown | 163 | Open. Recommend showing them as Texas's are shown, each labeled whose it is: a page change, a session of its own |
| 14 | The time spent in each status, in NYISO's words, is not on the page | 163 | Open. Recommend leaving it off while NYISO's terms hold the rows |
| 15 | A year held in part: the rule's hours and the foreseen load's differ | new | Open. Section 11, finding 1. Recommend giving the foreseen load the rule's budget in such a year |
| 16 | The do-file has never been run | new | Open. Yours |

## 11. Findings of this session

1. **In a year held in part, "if perfectly foreseen" is given fewer hours than the rule.** The rule may be off 100 hours of 2026; the foreseen load 76 (100 x the share of the year held). Effects on the page today, a load set to 100 hours:
   - New York City, real time, the year 2026 (chart and fold): the rule 63.93, "if perfectly foreseen" 63.97. The label is not true of that row.
   - `LZ_NORTH`, real time, last twelve months: foreseen 29.72 as shown; with the whole budget 29.29. "The rule kept 57 percent" would read 51. Bought day-ahead: 91 would read 84.
   - New York City, day-ahead: 74 would read 62. SP15, day-ahead: 71 would read 57.
   - The rule's own figures, which are the page's, do not move, and no flat figure does.
   - Not changed: the pro-rating is session 138's stated decision and the whole-year budget session 140's; which one yields is yours. Recommend the foreseen load take min(hours held, the rule's budget) in each year. Figures: `runs/session190/partial_year.out`.
2. **New York's real-time window is held in June 2026** by one incomplete month (edge case 3). Not an error of arithmetic; a consequence of "twelve months in a row" that no note stated.
3. **"How clean" reads 2024 for ERCOT** while the tight hours read 2025 (4.8). The mix tool's table holds eleven months of 2025. Each row names its year. Not changed.
4. **No error found in the default case.** Every hour equals the tables; the page, the CSV, the mirror and a second implementation agree.

## 12. The decisions on the page (session 462)

Session 462, 21 October 2026 (chain 019). The page lists, at its foot, every modelling choice it makes, one line each, with the session that made it and the ruling where one exists (`site/lib/decisions.ts`, `DATACENTER_DECISIONS`, drawn by `site/components/tool/DecisionsBlock.tsx`, `data-decisions="462"`). The list below is the same list, word for word; `tests/test_session462.py` holds the two to it. No figure moved: the block is words, and no number of the page reads it.

1. The cost is wholesale energy alone at a hub or load zone, bought every hour at the hour's price with no hedge. No delivery, transmission, capacity, ancillary or retail charge is added to it; a reader adds one as a scenario's "Delivery and other charges". (sessions 138 and 213)
2. A hub or load zone stands for the site: the price at one substation differs by congestion and losses, and no figure of the page is priced at a node. (session 138)
3. A month counts when 95 percent of its hours are held; the last twelve months are the newest twelve counted months in a row, each grid and region on its own months. (session 138)
4. A bad month is the top tenth of the 36 months that end with the last twelve, by nearest rank: the mirror of the battery page's 10th percentile month. (sessions 138 and 190)
5. Months and years are counted in the grid's standard time, with no daylight saving shift. (session 138)
6. A flexible load follows a rule decided before each hour from the prior 30 days of day-ahead prices, within a budget of hours each calendar year; it turns off whole and at once, with no minimum run. (session 140; the owner's ruling of 7 October 2026)
7. "If perfectly foreseen" chooses the same budget of hours knowing the year's prices, pro-rated in a year held in part (section 10, item 15, waits for a ruling). (session 138)
8. Power per GPU defaults to 1.3 kW (NVIDIA's DGX H100) and the overhead ratio to 1.56 (Uptime Institute, 2024); both are scenario A's assumptions since session 195. (sessions 138 and 195)
9. One page in the battery page's layout: what it will pay, whether the power is there, how clean it is and how soon it can be had, each computed for the load described, then the two scenarios and what matters most. (sessions 213 and 228)
10. Scenarios A and B are the block the three economics pages share; scenario A sets the headline. The contract's share and price are two of each scenario's assumptions, 0 by default, so the default load is fully merchant. (sessions 194, 195 and 213)
11. The cost of capital defaults to 9.6 percent, Lazard's weighted cost of a power plant's builder (60 percent debt at 8 percent, 40 percent equity at 12), labelled as a generator's, since no datacenter owner's rate is held. (sessions 196 and 265; the owner's rulings of 11 October 2026, and 7a of 18 October 2026)
12. Twenty years are counted, and the other charges, the change of prices and the upfront cost default to none: no cited figure is held for any of them. (session 194)
13. The scarcity level is USD 1,000 per MWh on every grid, said beside the count, with a grid's own scarcity signal as a second count where a table of it is held. (session 236; the owner's ruling of 12 October 2026)
14. Texas's delivery charges stand in their own table, one row a component, never added to the market cost; a line billed per kVA or per meter is marked conditional and left out of the first total. (sessions 236 and 265; ruling 1a of 18 October 2026)
15. A value typed outside its bounds is brought to the nearest bound, and a line says so. (session 265; ruling 8a of 18 October 2026)
16. A load that runs in fewer than one in ten of the hours held is said so under the headline. (session 298; ruling 5c of 18 October 2026)
17. The public statements on large loads are facts with a link to the document, with no quoted text. (session 265; the owner's ruling of 14 October 2026)
18. The scenarios are priced on the page's own last twelve months by default; another window is read from price_years_by_window, and a window a table does not hold is said, never computed. (session 352)
19. ERCOT's four summer peaks are shown for the flexible way and not counted by default, at the Commission's newest approved transmission rate and the newest summer held. (session 354)
20. A node's band (the resource nodes' day-ahead basis to the hub) is shown under the cost table and added to no figure: a load settles at its load zone. (session 354)
21. Capacity charges: none in ERCOT, an energy-only market; elsewhere "no public figure", because the auction results are held only in an internal table. (session 354)

Open choices stay in section 10 (the year held in part, item 15, among them); none of the lines above is a ruling this session made.

## Sign-off

Signing this note accepts, as the tool's rules: the 95 percent month; twelve counted months in a row; the bad month as the top tenth of 36 by nearest rank; standard time with no daylight saving shift; the rule's 30 prior days and its yearly budget; the two transmission figures for a flat load over 8,760 hours; and the two stated defaults. It leaves open the sixteen items of section 10. Since session 462 it accepts the decisions of section 12, the list the page shows at its foot, as well.

- Signed off by:
- Date:
- Items of section 10 ruled, and how:

## Checks

`tests/test_session190_replication.py`: the do-file's rules, parsed; the export (bytes, header, an unbroken run of hours, the twelve marked months); the CSV against the page's own files, hour by hour, and a planted error; the mirror against the page in Python and against node on `lib/datacenter.ts`; the rule and the foreseen load written a second time; where the tables are on the machine, every hour against them. `tests/test_session190.py`: this note's figures against the library; the page's links; the page's status unchanged; the tab. `site/scripts/check-datacenter-face.mjs`: the page in the internal view at 1280 and 390 px, the link, the three downloads. The earlier `tests/test_session138.py`, `test_session140.py`, `test_session163.py`, `site/scripts/check-datacenter.mjs`, `check-how-soon.mjs`, `test-datacenter.mjs`, `test-datacenter-rule.mjs` and `check-values.mjs`. Since session 194, for the scenarios of 4.14: `site/scripts/test-datacenter-finance.mjs`, `tests/test_session194.py` and `site/scripts/check-datacenter-scenarios.mjs`.
### Session 298: the owner's rulings of 18 October 2026 (the chain prompt of 19 October)

- **1a, 3a, 6a, 7a: as built**, nothing moved (the delivery table's two totals, each line's tariff on hover, the one paragraph on `large_load_public`, Lazard's 9.6 percent as the cost of capital).
- **5c:** one line under the headline when the load runs in under a tenth of the hours held: "This load ran in N percent of the hours held, fewer than one in ten: its price is the cheapest hours' alone, and a load that runs more would pay more" (`data-runs-little`, the share to a tenth of a percent). The share is `(held - down) / held` of the last twelve months' span (`lib/datacenter.ts`, `span`: the hours held and the hours the load was turned down). No figure moved.
- **8a:** a value typed outside a field's bounds is said under the field by the shared component itself (`components/decisions/ScenarioBlock.tsx`, `NumberField`: "99,999 was typed: the field runs from 0 to 10,000, so 10,000 is used."), with the page's own words where it gives them (the battery's, session 263); the battery page is checked unchanged (session 296's `check-battery-scenarios.mjs`). No figure moved.
- **The shared pieces of session 296** carried here where the page has the same element: the assumptions panel sits in a section that opens and closes, open to start, with one line of the scenario in view while closed (`ScenarioBlock`, `fold`); the generator page's two chart notes are hover tips beside their titles. This page's chart carries a legend and no note, so it has none to turn into a tip; the units toggle and the chart's table belong to session 303's one chart library.

### Session 354: the four summer peaks, a node's band and capacity charges (20 October 2026)

Three additions to "What a datacenter pays", each leaving every default figure as it was (check-values 1,377 of 1,377 on the economics pages; `check-datacenter-scenarios` and `check-datacenter-face` as before).

- **ERCOT's four summer peaks** (`loadModel()`, `cp`). ERCOT charges transmission on a load's demand in the four 15-minute intervals of June to September's monthly peaks, for the next year. The page reads every interval held in `ercot_4cp_intervals` (the data machine: seven summers, 2018 to 2025 without 2021; summer 2026 is not held yet) and maps each to its hour of the grid's standard-time year, `i = floor((t - 6 h - 1 January) / 1 h)`, where the flexible way's weight is read (the rule's own hours, the hours-off run beside a flat load). A summer's avoided share is `1 - mean of the four weights`; the saving is the newest summer's share times the Commission's newest approved postage stamp rate (2025: USD 68.547301 per kW of four-peak demand a year) times 1,000, USD per MW a year. With `cp=1` ("Four summer peaks" in the box) it is taken off the flexible way's cost at this site in scenario A and B; by default it is shown and not counted. The rate is the wholesale charge to the wires utilities; a retail customer pays it through its utility's transmission factor.
- **A node's band** (`nodeBand`). Under the cost table, the twelve months' mean of the 10th percentile, the median and the 90th percentile of every resource node's day-ahead basis to `HB_HUBAVG` (`node_basis_summary`, `dam_all_basis_<p>`), each month with its keys in a fold: USD -7.97, 0.31 and 7.39 per MWh over the twelve months shown. A load settles at its load zone; the band is what a site behind a generator's meter would see. Added to no figure.
- **Capacity charges**: a row of the cost table. ERCOT: none, an energy-only market whose four peaks set the transmission charge. Elsewhere "no public figure", with the reason: ISO-NE's and NYISO's auction results are held in `iso_all_capacity_prices`, an internal table not in the live set; CAISO's resource adequacy is bilateral and SPP has no capacity market, and no public price of either is held.

<a id="cross-checks"></a>

## Cross-checks

Session 196, 11 October 2026. The page's numbers are reproducible from its tables; here they stand beside what others publish, so that a reader sees each gap and its reason. Every published figure was read on 11 October 2026 from the address given, after the host's robots file and terms; no file of theirs is copied, the figure is quoted and the source linked. "Gap" is ours less theirs. A gap is not an error to be closed: most rows compare one modeled plant with a fleet, or a cost with a market's revenue, and the reason says which.

| Our figure | Published figure | Source and date | Gap | Reason |
|---|---|---|---|---|
| ERCOT, `LZ_NORTH`, real time, July 2026: USD 30.59 per MWh | Texas, industrial customers, July 2026: 7.07 cents per kWh, USD 70.70 per MWh (6.61 cents in July 2025) | [EIA, *Electric Power Monthly*, Table 5.6.A, July 2026](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a); the ERW holds the same figure, `eia_retail_electricity_prices`, `retail_price:TX:IND`, 2026-07, 70.7 (session 462) | -40.11 | Ours is wholesale energy alone at one load zone. EIA's is what every industrial customer of the state paid per kWh, all of it: energy as its supplier sold it, delivery and transmission, demand and other charges. The page's assumption "Delivery and other charges" is where a reader puts this gap; its default is none, and the Texas wires tariffs are listed under "What will it cost" |
| CAISO, SP15, real time, July 2026: USD 39.47 per MWh | California, industrial customers, July 2026: 25.11 cents per kWh, USD 251.10 per MWh | the same | -211.63 | The same, in a state whose delivery and public-purpose charges are several times the energy |
| NYISO, the New York City zone, day-ahead, July 2026: USD 77.45 per MWh | New York, industrial customers, July 2026: 10.81 cents per kWh, USD 108.10 per MWh | the same | -30.65 | The same; and EIA's is the whole state, where upstate industry buys cheaper power than the city's zone. Day-ahead is shown because July's real-time hours are held in part (289 of 744) |
| SP15, day-ahead, the peak block, January to September 2026: USD 24.04 per MWh over 166 delivery periods (a day, or two or three days sold as one) | USD 23.97, ICE's "SP15 EZ Gen DA LMP Peak" | [EIA, Wholesale Electricity and Natural Gas Market Data, the 2026 file of ICE hub prices](https://www.eia.gov/electricity/wholesale/) | +0.07; by month -0.77 to +0.83 | ICE's index is the volume-weighted price of trades made the day before for the peak block; ours is the mean of the cleared hourly day-ahead price over the same block (hours ending 7 to 22 Pacific, Monday to Saturday, NERC holidays out) on the same delivery days. A traded expectation against the cleared price: SP15's months agree within USD 1, single days differ by about USD 3 |
| NP15, the same: USD 34.35 per MWh over 73 delivery periods | USD 34.58, ICE's "NP15 EZ Gen DA LMP Peak" | [EIA, Wholesale Electricity and Natural Gas Market Data, the 2026 file of ICE hub prices](https://www.eia.gov/electricity/wholesale/) | -0.23; by month -2.10 to +1.40 | As in the row above: a traded expectation against the cleared price. NP15 trades on fewer days, so a month's mean rests on as few as three of them and differs by up to USD 2 |
| New England's internal hub, day-ahead, the peak block, January to September 2026: USD 77.72 per MWh over 157 delivery days | USD 78.55, ICE's "Nepool MH DA LMP Peak" | [EIA, Wholesale Electricity and Natural Gas Market Data, the 2026 file of ICE hub prices](https://www.eia.gov/electricity/wholesale/) | -0.83; by month -7.41 (January) to +1.31 | The same, with hours ending 8 to 23 Eastern, Monday to Friday. January's cold days were traded above where the day-ahead market cleared |
| Cost of capital, the default: 9.6 percent (0.6 x 8 + 0.4 x 12) | ATB, natural gas (quasi-merchant): term debt 7.5 percent, after-tax equity returns 8.5 percent | [NLR (formerly NREL), Annual Technology Baseline 2025, "Financial Cases and Methods"](https://atb.nlr.gov/electricity/2025/financial_cases_&_methods), read 21 October 2026 (session 448) | +2.1 points against the debt; +1.1 against the equity | The page's default is Lazard's pre-tax weighted cost for a power plant's builder; the ATB states the rates of a modeled gas plant's financing, after tax for equity. Neither is a datacenter owner's own rate, which no source held states |
| Years counted: 20 ("no cited term is held") | Lazard, gas combined cycle: facility life 30 years; ATB: cost recovery over 30 years for every technology | [Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), page 40; [Annual Technology Baseline 2025, "Financial Cases and Methods"](https://atb.nlr.gov/electricity/2025/financial_cases_&_methods), both read 21 October 2026 (session 448) | -10 years | Both are a generator's life or recovery period, not a buyer's contract term; the page counts a datacenter's years of power, for which no published term is held |

- Not compared: a price stated by a datacenter's own filing or press release. None was read: the ceiling of reads went to the sources above, and the repository holds tariffs (delivery charges), not a contract's price. For Samuel's ruling.
- Not compared: ERCOT's hubs and zones against ICE. EIA's 2026 file holds no ERCOT hub.
- Session 462 added the two rows above from session 448's reading of Lazard and the ATB (`docs/reviews/cross-checks-external.md`, rows D2 and D3), and noted that the EIA figures of the first three rows are held by the ERW itself. Session 448's row D1, the default against Lazard's own after-tax WACC of 7.7 percent, waits for Samuel's ruling on the default's label and is not a row yet.
- The hurdle rate's default, 9.6 percent, is Lazard's weighted cost for a power plant's builder ([Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), page 8). No published cost of capital of a datacenter's owner was read.

