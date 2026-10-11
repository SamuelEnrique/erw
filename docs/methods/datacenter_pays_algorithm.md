# What a datacenter pays: every number, step by step

Energy Research Warehouse (ERW), session 190, 11 October 2026. Written for sign-off. Page: `/cost-of-power`. This note is written from the code, not from the older notes: `warehouse/derived/datacenter_page.py` (the builder of the page's files), `warehouse/derived/price_compare.py` (the reader of the price tables and the rule for an hour), and on the site `lib/datacenter.ts` (all the arithmetic), `lib/datacenterdata.ts` (the files) and `app/cost-of-power/`. Where the older note and the code differ, section 9 says so. The older note, [`datacenter_cost.md`](datacenter_cost.md), stays as the record of why each piece was built, of every source's terms and of the blocks this page borrows from other tools.

Downloads, the default case hour by hour: [erw_2026_datacenter_hourly.csv](/datacenter/erw_2026_datacenter_hourly.csv), [the Stata do-file](/datacenter/erw_2026_datacenter_replication.do) and [its Python mirror](/datacenter/erw_2026_datacenter_replication.py). Section 8.

**The default case**, used for every example below: ERCOT, the North load zone (`LZ_NORTH`), a flat load of 100 MW, bought in real time, 1.3 kW per GPU, an overhead ratio of 1.56. With the page's files built on 10 October 2026 the page shows: USD 33.73 per MWh over the last twelve months (October 2025 to September 2026), USD 29.55 million for 876,000 MWh; a bad month of USD 37.88 per MWh (August 2026, of 36 months); USD 0.0684 per GPU-hour, 49,310 GPUs; the hub beside the zone (`HB_NORTH`) at USD 32.51, so the zone is 1.22 above its hub.

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
- **Delivery and transmission, Texas** (rows of their own, never added to the market cost). Each charge is printed as its tariff prints it (`texas_delivery_charges`, 41 rows of four utilities; `texas_transmission_matrix`). Two figures are computed:
  - **The transmission factor alone, a flat load** = factor (USD per kW of four-coincident-peak demand a month) x 12 x 1,000 / 8,760, USD per MWh. A flat load's demand in those four intervals is its size. Computed only where the factor is printed per kW: Oncor 6.260839 gives 8.58; AEP Texas 5.956038 gives 8.16. CenterPoint's and Texas-New Mexico Power's are printed per kVA and are not converted.
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

The reader types a share s of the energy (percent, held between 0 and 100) and a price c (USD per MWh). Over the load's last twelve months, with E = sum of `energy` x MW and K = sum of `cost` x MW (`contractResult`):

- contracted energy costs s x E x c; the rest pays the market, (1 - s) x K; the total is their sum, and per MWh the total / E;
- without the contract: K, and K / E;
- a bad month with the contract: s x c + (1 - s) x the bad month's price per MWh.

Default with 50 percent at USD 30: 0.5 x 876,000 x 30 = 13,140,000; 0.5 x 29,546,505 = 14,773,252.50; together USD 27,913,252.50, or 31.86 per MWh against 33.73. Not in it: shape, settlement point, collateral, term.

### 4.11 The folds

- **Every year, every month:** the figures of 4.6 and 4.1 for each year and month held, the incomplete ones muted, with the hours off and the months or hours held.
- **Every region of the grid, a flat load:** each region's own last twelve months in the market chosen, with the months they are. Regions of one grid can stand on different months (section 6, item 5).
- **The Commission's transmission charge matrix:** as printed.

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
| Scenarios: hurdle rate (session 194) | 8 percent | no cited rate is held; set equal to the interest rate of Lazard's cost cases, "60% debt at an 8% interest rate"; to be confirmed by the owner (4.14) |

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

## Sign-off

Signing this note accepts, as the tool's rules: the 95 percent month; twelve counted months in a row; the bad month as the top tenth of 36 by nearest rank; standard time with no daylight saving shift; the rule's 30 prior days and its yearly budget; the two transmission figures for a flat load over 8,760 hours; and the two stated defaults. It leaves open the sixteen items of section 10.

- Signed off by:
- Date:
- Items of section 10 ruled, and how:

## Checks

`tests/test_session190_replication.py`: the do-file's rules, parsed; the export (bytes, header, an unbroken run of hours, the twelve marked months); the CSV against the page's own files, hour by hour, and a planted error; the mirror against the page in Python and against node on `lib/datacenter.ts`; the rule and the foreseen load written a second time; where the tables are on the machine, every hour against them. `tests/test_session190.py`: this note's figures against the library; the page's links; the page's status unchanged; the tab. `site/scripts/check-datacenter-face.mjs`: the page in the internal view at 1280 and 390 px, the link, the three downloads. The earlier `tests/test_session138.py`, `test_session140.py`, `test_session163.py`, `site/scripts/check-datacenter.mjs`, `check-how-soon.mjs`, `test-datacenter.mjs`, `test-datacenter-rule.mjs` and `check-values.mjs`. Since session 194, for the scenarios of 4.14: `site/scripts/test-datacenter-finance.mjs`, `tests/test_session194.py` and `site/scripts/check-datacenter-scenarios.mjs`.
<a id="cross-checks"></a>

## Cross-checks

Session 196, 11 October 2026. The page's numbers are reproducible from its tables; here they stand beside what others publish, so that a reader sees each gap and its reason. Every published figure was read on 11 October 2026 from the address given, after the host's robots file and terms; no file of theirs is copied, the figure is quoted and the source linked. "Gap" is ours less theirs. A gap is not an error to be closed: most rows compare one modeled plant with a fleet, or a cost with a market's revenue, and the reason says which.

| Our figure | Published figure | Source and date | Gap | Reason |
|---|---|---|---|---|
| ERCOT, `LZ_NORTH`, real time, July 2026: USD 30.59 per MWh | Texas, industrial customers, July 2026: 7.07 cents per kWh, USD 70.70 per MWh (6.61 cents in July 2025) | [EIA, *Electric Power Monthly*, Table 5.6.A, July 2026](https://www.eia.gov/electricity/monthly/epm_table_grapher.php?t=epmt_5_6_a) | -40.11 | Ours is wholesale energy alone at one load zone. EIA's is what every industrial customer of the state paid per kWh, all of it: energy as its supplier sold it, delivery and transmission, demand and other charges. The page's assumption "Delivery and other charges" is where a reader puts this gap; its default is none, and the Texas wires tariffs are listed under "What will it cost" |
| CAISO, SP15, real time, July 2026: USD 39.47 per MWh | California, industrial customers, July 2026: 25.11 cents per kWh, USD 251.10 per MWh | the same | -211.63 | The same, in a state whose delivery and public-purpose charges are several times the energy |
| NYISO, the New York City zone, day-ahead, July 2026: USD 77.45 per MWh | New York, industrial customers, July 2026: 10.81 cents per kWh, USD 108.10 per MWh | the same | -30.65 | The same; and EIA's is the whole state, where upstate industry buys cheaper power than the city's zone. Day-ahead is shown because July's real-time hours are held in part (289 of 744) |
| SP15, day-ahead, the peak block, January to September 2026: USD 24.04 per MWh over 166 delivery periods (a day, or two or three days sold as one) | USD 23.97, ICE's "SP15 EZ Gen DA LMP Peak" | [EIA, Wholesale Electricity and Natural Gas Market Data, the 2026 file of ICE hub prices](https://www.eia.gov/electricity/wholesale/) | +0.07; by month -0.77 to +0.83 | ICE's index is the volume-weighted price of trades made the day before for the peak block; ours is the mean of the cleared hourly day-ahead price over the same block (hours ending 7 to 22 Pacific, Monday to Saturday, NERC holidays out) on the same delivery days. A traded expectation against the cleared price: SP15's months agree within USD 1, single days differ by about USD 3 |
| NP15, the same: USD 34.35 per MWh over 73 delivery periods | USD 34.58, ICE's "NP15 EZ Gen DA LMP Peak" | [EIA, Wholesale Electricity and Natural Gas Market Data, the 2026 file of ICE hub prices](https://www.eia.gov/electricity/wholesale/) | -0.23; by month -2.10 to +1.40 | As in the row above: a traded expectation against the cleared price. NP15 trades on fewer days, so a month's mean rests on as few as three of them and differs by up to USD 2 |
| New England's internal hub, day-ahead, the peak block, January to September 2026: USD 77.72 per MWh over 157 delivery days | USD 78.55, ICE's "Nepool MH DA LMP Peak" | [EIA, Wholesale Electricity and Natural Gas Market Data, the 2026 file of ICE hub prices](https://www.eia.gov/electricity/wholesale/) | -0.83; by month -7.41 (January) to +1.31 | The same, with hours ending 8 to 23 Eastern, Monday to Friday. January's cold days were traded above where the day-ahead market cleared |

- Not compared: a price stated by a datacenter's own filing or press release. None was read: the ceiling of reads went to the sources above, and the repository holds tariffs (delivery charges), not a contract's price. For Samuel's ruling.
- Not compared: ERCOT's hubs and zones against ICE. EIA's 2026 file holds no ERCOT hub.
- The hurdle rate's default, 9.6 percent, is Lazard's weighted cost for a power plant's builder ([Lazard, *Levelized Cost of Energy+*, June 2025](https://www.lazard.com/media/uounhon4/lazards-lcoeplus-june-2025.pdf), page 8). No published cost of capital of a datacenter's owner was read.

