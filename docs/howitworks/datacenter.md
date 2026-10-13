# How it works: What a datacenter pays

- Address: `/cost-of-power` (the first tab of the cost of power, beside "What a generator earns" and "What a battery earns").
- Status: in review, as every page of the site is (`site/lib/release.ts`). A visitor sees the short "in review" page; the tool opens in the internal view only.
- Written by session 249 from the branch `origin/wip/236-datacenter`, commit `d4eaec68` (session 236), and checked again by session 260 against `main` at `34b468fa`. The page landed on 13 October 2026 as `aa3addbc` (09:14 UTC, sessions 235 and 236 together).
- What changed on the page after `d4eaec68`, all of it on `main`: the hourly carbon sentence names no length of window (`bba5d091`); and ERCOT's reserve adder is counted on the page (session 236's follow-up, landed as `01161064` at 10:57 UTC), where the page first said the count was "coming". Questions 7 and 9 and the demo give the page as it is now.
- Date: 2026-10-13. Every figure below is the default case as the repository's files state it on 10 to 13 October 2026. The page's price files are rebuilt daily (on `main` they were built 2026-10-13T17:37:23Z), so the screen can differ from this page; the screen is then the newer.

## 1. What it is for, and for whom

The tool answers four questions for a load the reader describes, then compares two options.

1. What will it pay? Wholesale energy at one hub or load zone, hour by hour, in USD per MWh, in USD for the size, and per GPU-hour.
2. Will the power be there? The hours of the last twelve months priced at or above USD 1,000 per MWh, and what a flat load paid in them.
3. How clean? The CO2 per MWh of the grid's consumed electricity, weighted by the load's own energy.
4. How soon? The operator's own figures of large load approved and running, where a public table holds them. No wait is estimated.
5. Which option is better? Scenarios A and B: two sites, or two contracts, or two ways of running.
6. What matters most. One chart: how far each assumption moves the all-in power cost per GPU-hour.

Who it serves: a buyer of power for a large load (a datacenter developer, an AI company's energy lead), an investor who has to test a site's power cost, and an operator who wants to see what flexibility is worth.

What it is not: a quote, a tariff calculator or a forecast. The headline is market energy alone. The default case reads USD 33.73 per MWh; Texas industrial customers paid USD 70.70 per MWh in July 2026 by EIA's count (section 4). The page says so in one sentence under its cost table.

Grids: ERCOT, CAISO, NYISO, ISO-NE and SPP. MISO is listed and blank ("paused while terms are reviewed"). PJM is listed and blank ("licensed source needed").

A second view, "Grid by grid" (`?view=grids`), is an older model with its own method (`docs/methods/cost_of_power.md`). It shares no number with the view described here.

## 2. The model, in numbered steps

The default case, used for every example: ERCOT, the North load zone (`LZ_NORTH`), a flat 100 MW load, bought in real time, 1.3 kW per GPU, an overhead ratio of 1.56.

1. **The price tables.** Connectors write each grid's public hub and zone prices to the warehouse. A builder (`warehouse/derived/datacenter_page.py`) turns every series into one price an hour and writes one file per grid and year under `site/data/datacenter/`. It makes no request.
2. **An hour's price.** A day-ahead price is hourly and is taken as it is. A real-time price is the mean of the hour's four 15-minute prices, and the hour is held only when all four are there. The price is rounded to the cent. Nothing is filled: a missing hour is left out of every sum.
3. **The clock.** Hours are counted in the grid's standard time all year, with no daylight saving shift (ERCOT and SPP: UTC less 6 hours; CAISO less 8; NYISO and ISO-NE less 5). Every day has 24 hours.
4. **The load's shape.** Each hour gets a weight: 1 for a flat load, 0 when a flexible load is off, between 0 and 2 for a load that shifts energy within the day. The reader picks the shape under "How it runs".
5. **Months.** For each month the model sums price times weight (the cost per MW) and the weights (the energy). A month counts only when at least 95 percent of its hours hold a price.
6. **The last twelve months.** The newest twelve counted months in a row. Cost over energy is the headline: 295,465.05 / 8,760 = USD 33.73 per MWh. Times 100 MW: USD 29.55 million for 876,000 MWh.
7. **A bad month.** The 36 months ending with those twelve are ranked by cost per MWh; the month at the top tenth, by nearest rank, is shown. Default: August 2026, USD 37.88, fourth of 36.
8. **Per GPU-hour.** Price x kW per GPU x overhead ratio / 1,000. Default: 33.7289 x 1.3 x 1.56 / 1,000 = USD 0.0684. The same 100 MW powers 49,310 GPUs.
9. **Capacity and ancillary charges.** None is added. ERCOT has no capacity market; its scarcity pricing is already inside the energy price. For NYISO and ISO-NE, which hold capacity auctions, the tool adds no capacity charge and reads no capacity or ancillary table.
10. **Delivery and tariff riders (Texas only).** The tariff lines of four wires utilities are turned into USD per MWh for a flat load and summed by component: transmission, distribution, other riders. They stand in their own table and are never added to the market cost. For Oncor at 100 MW the total is USD 8.81 per MWh. Other grids read "not held yet".
11. **Flexibility.** A flexible load follows a rule an operator could follow: it is off in an hour whose day-ahead price, published the day before, is at or above a threshold set from the prior 30 days, until its yearly budget of hours is used. It pays the price of the market it buys in. Off in 100 hours a year, the default case pays USD 31.46 per MWh, 2.27 less than flat. The same load "if perfectly foreseen" stands beside it: USD 29.72, a bound and not a plan.
12. **Scarce hours.** The model counts the hours of the twelve months priced at or above USD 1,000 per MWh, sums what a flat load paid in them, and says in how many each way of running was off. Default: 4 hours, all in January 2026, USD 446,175 for 100 MW. For ERCOT a second count stands beside it: the hours in which ERCOT's own reserve adder (the hour's mean of the on-line adder of its operating reserve demand curve) was at or above USD 100 per MWh, over the part of the twelve months ERCOT published it, and over the last year it was published.
13. **Carbon.** Each month's energy is multiplied by the grid's monthly carbon intensity of consumed electricity (EIA-930's CO2 estimates). Default: 303.14 kg of CO2 per MWh, 265,548 tonnes a year for 100 MW. A second figure weights the hourly intensity by the load's hourly weights over the hours the hourly table holds.
14. **Large load (ERCOT only).** The model reads ERCOT's monthly status reports as a table and shows the latest: megawatts approved to energize, megawatts observed running, and the change against a report a year or more earlier.
15. **The second site.** Scenario B can stand at another zone, hub or grid (`bsite=<grid>:<region>`). Steps 2 to 8, 12, 13 and 14 are run again for that site over that site's own last twelve months.
16. **The scenarios.** In the browser, ten assumptions per scenario turn the year's cost into a present value, a fixed price with the same present value, and an all-in cost per GPU-hour. The last twelve months are repeated every year, changed only by the rate the reader types. Nothing is sent.
17. **The sensitivity chart.** Each assumption of the scenario in view is moved one step down and one step up, the others held, and the all-in cost per GPU-hour is recomputed. The longest bars come first.

So a price becomes a dollar per MWh this way: four 15-minute prices become an hour; hours times the load's weights become a month; twelve counted months become the headline. Nothing else is added on the way.

## 3. Every assumption, its default and its source

"Fixed" means the reader cannot change it on the page. Address names are the query-string parameters.

### The reader's load ("Your load")

| Assumption | Default | Where the user changes it | Source |
|---|---|---|---|
| Grid | ERCOT | "Grid" (`grid`) | ERW's choice: the first grid of the page's list (`ORDER` in `site/lib/datacenter.ts`); its hubs and load zones are held from 2015 |
| Region | the grid's main region: `LZ_NORTH`, `TH_SP15_GEN-APND`, `N.Y.C.`, `.H.INTERNAL_HUB`, `SPPNORTH_HUB` | "Region" (`region`) | The owner's ruling (session 140): a Texas load settles at its load zone, not at a hub. `docs/methods/datacenter_cost.md` |
| Size | 100 MW, bounds 0.1 to 10,000 | "Size, MW" (`mw`) | ERW's choice. Every USD and MWh figure is the per-MW figure times the size |
| How it runs | flat | "How it runs" (`run`: `flat`, `hours`, `share`, `shift`) | ERW's choice |
| Hours off a year | 100, bounds 0 to 8,784 | "hours a year" (`n`) | ERW's choice (`DEFAULTS` in `site/lib/datacenter.ts`) |
| Share of hours off | 5 percent | "percent of hours" (`pct`) | ERW's choice |
| Share of a day's energy shifted | 20 percent, bounds 0 to 50 | "percent of a day's energy" (`shift`) | ERW's choice |
| How it buys | real time; day-ahead when the address names no market and real time holds no twelve counted months | "How it buys" (`buy`: `rt`, `da`) | ERW's choice |

### The scenarios (each for A and for B)

| Assumption | Default | Where the user changes it | Source |
|---|---|---|---|
| How the load runs | as "Your load" | "How the load runs" (`aw`, `bw`: 0 flat, 1 flexible) | the reader's own input |
| Power per GPU | 1.3 kW, bounds 0.05 to 20 | "Power per GPU" (`ag`, `bg`) | NVIDIA DGX H100 datasheet: 8 GPUs, maximum system power 10.2 kW, so about 1.3 kW per GPU with its share of the server |
| Facility overhead ratio (PUE) | 1.56, bounds 1 to 3 | "Facility overhead ratio (PUE)" (`ap`, `bp`) | Uptime Institute, Global Data Center Survey 2024, the industry average. Google reports 1.09 for its fleet |
| Delivery and other charges | USD 0 per MWh, bounds 0 to 500 | "Delivery and other charges" (`ad`, `bd`) | ERW's choice: the page's figure is market energy alone. To count Texas's delivery, the reader types the table's total here |
| Change of prices | 0 percent a year, bounds -20 to 20 | "Change of prices" (`ae`, `be`) | none held: no cited forecast, so the last twelve months are repeated |
| Upfront cost | USD 0 per kW, bounds 0 to 20,000 | "Upfront cost" (`au`, `bu`) | none held |
| Years counted | 20, bounds 1 to 40 | "Years counted" (`al`, `bl`) | none held: no cited term for a datacenter's power |
| Hurdle rate | 9.6 percent, bounds 0 to 40 | "Hurdle rate" (`ah`, `bh`) | Lazard, Levelized Cost of Energy+, June 2025: "60% debt at an 8% interest rate and 40% equity at a 12% cost", 0.6 x 8 + 0.4 x 12. A power plant builder's cost of capital; none is cited for a datacenter's own |
| Contract share | 0 percent of the energy | "Contract share" (`an`, `bn`) | ERW's choice: fully merchant by default |
| Contract price | USD 0 per MWh, bounds 0 to 1,000 | "Contract price" (`ac`, `bc`) | the reader's own term; no published contract price is held |
| Scenario B's site | the same site as A | "Scenario B's site" (`bsite=<grid>:<region>`) | session 236 (`SITE_B` in `site/lib/datacenter/finance.ts`) |
| The contract's form | a flat share of every hour's energy at one fixed price for every year counted | fixed | ERW's choice. No shape, settlement point, collateral or term |
| What changes by the yearly rate | the market's cost and the other charges; the contract's price does not | fixed | `costInYear` in `finance.ts` |
| Rate of return on an extra upfront cost | found by bisection between -99 and 1,000 percent a year | fixed | `IRR_LOW`, `IRR_HIGH` in `finance.ts` |
| Sensitivity steps | 0.1 kW; 0.1 of overhead ratio; USD 5 per MWh; 1 point of price change; USD 100 per kW; 5 years; 1 point of hurdle rate; 10 points of contract share; USD 1 of contract price | fixed | ERW's choice (`SPECS` in `finance.ts`) |

Two files state the hurdle rate differently. `docs/methods/datacenter_cost.md` and section 7 of `docs/methods/datacenter_pays_algorithm.md` still say 8 percent. Section 4.14 of the same note and the code (`HURDLE = 9.6`) say 9.6, since session 196. The code is the newer.

### Fixed rules of the cost model

| Assumption | Default | Where the user changes it | Source |
|---|---|---|---|
| A month counts | at 95 percent of its hours | fixed | ERW's choice (`NEAR = 0.95`); no outside source |
| The last twelve months | twelve counted months in a row | fixed | ERW's choice. One missing month holds the window in place (New York, real time, below) |
| A bad month | the top tenth of the last 36 months, nearest rank | fixed | ERW's choice, the mirror of the battery page's worst-tenth month |
| Standard time | no daylight saving shift; offsets 6, 8 and 5 hours | fixed | ERW's choice: every day has 24 hours |
| A real-time hour | the mean of four 15-minute prices, all four needed, rounded to the cent | fixed | ERW's rule. Over the default case's 103,055 hours rounding moves the mean by USD 0.00004 per MWh |
| The rule's memory | the prior 30 days of day-ahead prices; a day is decided only when 684 of those 720 hours are held | fixed | ERW's choice (`PRIOR_DAYS = 30`) |
| The rule's threshold | the k-th dearest of those prices; k = 8 for 100 hours a year | fixed | `ruleThresholds` in `site/lib/datacenter.ts` |
| The rule's budget | the hours named, each calendar year | fixed | session 140; the owner's ruling of 7 October 2026 |
| A load turns off whole, at once, with no minimum | by construction | fixed | no source; a real load has a minimum and takes time to stop and start |
| Wholesale energy only | no delivery, capacity, ancillary, uplift, retail margin or tax | fixed (the reader may type "Delivery and other charges") | by construction |
| A hub or zone is not a site | no basis to the load's own node | fixed | by construction |
| The other way of running, when "Your load" is flat | off in 100 hours a year | fixed | the form's default (`altFlex` in `model.ts`) |

### Fixed rules of the three answers and of the delivery table

| Assumption | Default | Where the user changes it | Source |
|---|---|---|---|
| The scarcity level | USD 1,000 per MWh, every grid | fixed | FERC Order 831's cap on an incremental energy offer; the owner's ruling of 12 October 2026 (`SCARCITY_USD` in `answers.ts`). ERCOT is outside FERC; the page states its cap as USD 5,000 |
| ERCOT's own signal | the reserve adder's hourly mean at or above USD 100 per MWh; counted only where ERCOT published it (to 4 December 2025); the reliability deployment adder is not counted or joined | fixed | `ADDER_USD` in `site/lib/datacenter/answers.ts`; `ercot_rtm_price_adders`; `docs/methods/datacenter_pays_algorithm.md`, section 4.15. "Above zero" would mislead: it is mostly fractions of a cent |
| The ways compared in the answers | flat; flexible (the load's own, else 100 hours); shifting (the load's own, else 20 percent) | through "Your load" | `waysOf` in `answers.ts` |
| Carbon basis | consumed electricity (`intensity_demand`: generation plus imports less exports), the balancing authority's average | fixed | `carbon_intensity_monthly`, `carbon_intensity_hourly`; `docs/methods/emissions.md`. Not the marginal plant |
| Balancing authority for each grid | ERCO, CISO, NYIS, ISNE, SWPP | fixed | EIA-930 (`BA` in `answers.ts`) |
| Twelve-month carbon | the monthly average, over the months the table holds | fixed | session 228, decision 4 |
| Carbon trend's two ends | the first and last year with at least ten months held | fixed | ERW's choice (`LoadAnswers.tsx`) |
| Large load change | from the newest report a year or more before the latest; else the earliest held | fixed | `largeLoad` in `answers.ts` |
| The live set's reads | cached one hour | fixed | `HOURLY` in `site/lib/supabase.ts` |
| Hours in a year for delivery | 8,760, in a leap year too | fixed | `YEAR_HOURS` in `delivery.ts` |
| A flat load's demand in the four coincident peaks, and its billing demand | its size | fixed | by construction. A load off in those intervals pays less; not computed |
| A kVA | counted as a kW (a power factor of 1) | fixed | session 236, decision 4. Awaiting the owner's ruling |
| Accounts and meters | one account with one meter | fixed | session 236, decision 5 |
| Lines that apply only to some loads | left out of the sums (3 of 41 lines) | fixed | the tariff's own words; awaiting the owner's ruling |
| Service voltage | transmission voltage | fixed | the rate class a large load takes (`texas_delivery_charges`) |
| The Commission's wholesale rate per MWh | rate x 1,000 / 8,760 | fixed | Public Utility Commission of Texas, Docket 57491 (2025, approved) and Docket 59080 (2026, filed, not approved) |

### The view "Grid by grid" (another model)

| Assumption | Default | Where the user changes it | Source |
|---|---|---|---|
| Facility size | 100 MW | its calculator | `docs/methods/cost_of_power.md` |
| Load factor | 0.9 | its calculator | the same |
| Period | a month (30 days), a year (365 days) or a run of 90 days | its calculator | the same |
| Flexible case | the cheapest 80 percent of hours, by hour of day and month | fixed | the same |

## 4. The cross-checks

"Gap" is ours less theirs. A gap is not an error to close: the reason says what each side measures.

| What is compared | Ours | Theirs | Gap | Reason | Where it is written |
|---|---|---|---|---|---|
| ERCOT `LZ_NORTH`, real time, July 2026, against Texas industrial customers (EIA, Electric Power Monthly, Table 5.6.A) | USD 30.59 per MWh | USD 70.70 per MWh | -40.11 | Ours is wholesale energy at one zone. EIA's is everything an industrial customer paid: supply, delivery, demand and other charges | `datacenter_pays_algorithm.md` (branch), "Cross-checks" |
| CAISO SP15, real time, July 2026, against California industrial customers (the same table) | 39.47 | 251.10 | -211.63 | The same, in a state whose delivery and public-purpose charges are several times the energy | the same |
| NYISO New York City zone, day-ahead, July 2026, against New York industrial customers (the same table) | 77.45 | 108.10 | -30.65 | The same; EIA's is the whole state. Day-ahead is used because July's real-time hours are held in part (289 of 744) | the same |
| SP15 day-ahead peak block, January to September 2026, against ICE's "SP15 EZ Gen DA LMP Peak" (EIA's file of ICE hub prices) | 24.04 over 166 delivery periods | 23.97 | +0.07; by month -0.77 to +0.83 | A traded expectation against the cleared price | the same |
| NP15, the same block, against ICE's "NP15 EZ Gen DA LMP Peak" | 34.35 over 73 delivery periods | 34.58 | -0.23; by month -2.10 to +1.40 | The same; NP15 trades on fewer days | the same |
| New England internal hub, day-ahead peak, against ICE's "Nepool MH DA LMP Peak" | 77.72 over 157 delivery days | 78.55 | -0.83; by month -7.41 to +1.31 | The same; January's cold days traded above where the market cleared | the same |
| Each hour of the default case against the warehouse's price tables | 103,055 hours | the tables' 412,220 real-time rows | none above half a cent | The builder against the tables, read as text | the same note, section 3 |
| The page against its replication CSV and Python mirror | 33.73; 37.88; 0.0684; 32.51 | the same four | 0 | The same cents summed in the same months. The Stata do-file has never been run | the same note, section 8 |
| Every checked number against a second read of the live set (`check-values.mjs`) | 477 values | 477 of 477 at 07:02 UTC; 471 of 477 on the final build at 07:34 UTC | 6 | The six are the hourly carbon window: the live set's table grew during the session and the page served its cached read | `runs/session249/code_report_236.md`, "Checks" |
| The same check on the whole site at the two landings of 13 October | every keyed value of every page | 4,249 of 4,249 (09:14 UTC); 4,590 of 4,590 (10:57 UTC) | 0 | `check-datacenter-scenarios` 119 of 119 and `check-datacenter-face` 23 of 23 at the first | `archive/sessions/SESSION_236_REPORT.md`, `archive/sessions/SESSION_237_REPORT.md`, "The landing" |
| The 16 delivery figures against a second computation in Python | Oncor 8.81, CenterPoint 7.67 | the same | 0 | `tests/test_session236.py` on the branch | the same report, item 6 of "What was done" |
| Numbers that were on the page before session 236 | 57 of 57 identical at 1280 and 390 px | | 0 moved | The brand and the new tables moved no figure | `docs/brand/review-236/numbers_before_after.txt` (branch) |

Not compared, and said so in the note: a price from a datacenter's own filing or press release (none was read); ERCOT's hubs and zones against ICE (EIA's 2026 file holds no ERCOT hub); a datacenter owner's cost of capital (none was read).

## 5. What it cannot see, ranked by how much it moves the answer

Biggest first. The size is given where the repository holds a number.

1. **Everything on the bill that is not wholesale energy.** Size: USD 40.11 per MWh in Texas in July 2026 (EIA's 70.70 against the tool's 30.59), 211.63 in California, 30.65 in New York. The tool itemizes one part of it, for Texas only: delivery of USD 7.10 to 8.81 per MWh across the four utilities at 100 MW. For the rest (a retailer's margin, hedging, ancillary services, uplift, taxes): no number held.
2. **Future prices.** The tool repeats the last twelve months. Size: a flat load at `LZ_NORTH` paid from USD 21.68 per MWh (2016) to 150.61 (2021, Winter Storm Uri) by calendar year, against 33.73 now. Prices rising 2 percent a year lift the fixed price with the same present value from 33.73 to 38.66. No forecast is held.
3. **The actual tariff or contract a large load negotiates.** The contract on the page is a flat share at one price. A real one has a shape, a settlement point, collateral and a term; a large-load tariff can carry minimum demand and exit terms. No number held.
4. **Transmission cost allocation: ERCOT's four coincident peaks.** The tool counts a flat load's demand in the four summer peak intervals as its size. Size at stake: the transmission component, USD 6.92 to 8.58 per MWh by utility. A load off in those four intervals pays less; that is not computed. The saving a real load could reach: no number held.
5. **Capacity charges outside ERCOT.** NYISO and ISO-NE hold capacity auctions whose cost reaches load. The tool adds none. A load's capacity bill depends on its peak contribution and the reserve requirement: no number held. New York's gap in item 1 includes it.
6. **Basis from the hub or zone to the load's own node.** Size held for hub to zone only: `LZ_NORTH` is USD 1.22 per MWh above `HB_NORTH`; `LZ_WEST` reads 35.27 beside `HB_WEST` at 30.66. Zone to node (congestion and losses at one substation): no number held.
7. **What flexibility a real load can deliver.** The modeled load turns off whole, at once, with no minimum. Size of the modeled saving: USD 2.27 per MWh under the rule and 4.01 if perfectly foreseen, for 100 hours a year. In 2021 the same load paid 136.09 under the rule and 49.86 if foreseen, against 150.61 flat. What a load with a minimum and a restart time would keep: no number held.
8. **The interconnection wait.** No wait is estimated, for any grid. It moves no USD per MWh figure on the page; it moves the year in which any of them starts. Size in USD: no number held. What the repository holds is in section 6, question 6.
9. **Behind-the-meter supply.** On-site generation or storage is not modeled, and the tool's method notes do not mention it. No number held.
10. **Curtailment and physical shortage.** The scarce-hour count is a count of prices, and ERCOT's adder count is a count of a price adder that ended on 4 December 2025. Neither says whether a load would have been shed, and no operator notice is held for ERCOT. What ERCOT's real-time ancillary prices have signalled since 5 December 2025: not held. No number held.
11. **Marginal carbon and the energy actually bought.** The carbon figure is the grid's average for consumed electricity, not the marginal plant and not a claim about a purchase. Size of the choice of window alone: the hourly figure read 346.71 kg per MWh over 776 hours and 313.05 over 10,144 hours (section 6, question 9).
12. **Stale or thin history.** New York's real-time prices lack 19 days of July 2026, so its real-time window stays July 2025 to June 2026 (USD 68.49 at New York City; day-ahead reads 73.10). ERCOT's load zone prices stopped at 3 October 2026 when the note was written on 11 October. Each figure names its months.

## 6. The ten hardest questions

1. **Is USD 33.73 per MWh what my datacenter would pay?**
   No. It is what a flat 100 MW load paid for wholesale energy at `LZ_NORTH` in real time from October 2025 to September 2026, with no hedge. Texas industrial customers paid USD 70.70 per MWh in July 2026 by EIA's count; the tool's figure for that month is 30.59. For a load in Oncor's area the page adds a delivery total of USD 8.81 per MWh in its own table. The rest of the gap the tool does not know. It would need the retail supply contract and the large-load tariff the site would take.

2. **Scenario B in California shows USD 28.58 against Texas's 33.73. Is California cheaper?**
   For wholesale energy at SP15 over its own last twelve months, yes: USD 24.97 million a year for 100 MW against 29.55 million. For a delivered bill, no number on the page says so, and EIA's count says the opposite: California industrial customers paid USD 251.10 per MWh in July 2026 against 39.47 at SP15. The delivery table exists for Texas only; for California it reads "not held yet".

3. **What will power cost over the twenty years you discount?**
   The tool does not know. It repeats the last twelve months and changes them by the rate you type; the default rate is 0 because no cited forecast is held. History at this zone by year: 24.04 (2015), 21.68, 23.88, 30.82, 36.35, 21.82, 150.61 (2021), 62.93, 48.69, 26.41, 32.66 (2025), and 34.02 for nine months of 2026. A forward curve or a cited forecast would be needed.

4. **Can I cut the transmission charge by being off in the four coincident peaks?**
   The tool does not compute it. It assumes a flat load's demand in those four intervals is its size, which gives Oncor's transmission component of USD 8.58 per MWh (factor 6.260839 x 12,000 / 8,760) and AEP Texas's 8.16. The method note says a load off in those intervals pays less. To put a number on it the tool would need each year's four intervals and the load's draw in them. Two more cautions: CenterPoint's and Texas-New Mexico Power's factors are printed per kVA and counted at a power factor of 1, and Texas-New Mexico Power's factor (sheet effective 1 September 2025) is probably superseded.

5. **Where are capacity and ancillary charges?**
   Not in any figure. In ERCOT there is no capacity market, and scarcity pricing is already inside the energy price. In NYISO and ISO-NE a capacity cost reaches load and the tool adds none; the warehouse holds auction prices (`iso_all_capacity_prices`, internal) and the page does not read them. Ancillary and uplift charges allocated to load: no number held. The reader can type a figure under "Delivery and other charges".

6. **How long until a new large load is energized?**
   The tool does not know and estimates no wait: no operator publishes one. For ERCOT it shows the operator's own report of 19 June 2026: 8,927 MW approved to energize, 3,900 MW observed running, the approved figure up 2,053 MW since the report of 28 May 2025; and 137 new submissions totalling about 140,000 MW by 13 March 2026. (The method note, written earlier the same night, quotes the 26 March 2026 report: 9,042 MW and 4,004 MW, up 2,168; the live set gained three reports during session 228, so June is the newer.) The download `tables.csv` holds the entities' own figures: Oncor's 825 days on average and 687 at the median from first submission to energizing, and ERCOT's "approximately 220 days" of delay against in-service dates. ERCOT's slides of 26 August 2026 say it paused approvals to energize datacenters of 75 MW or more on 3 August 2026 (`docs/methods/ercot_large_load_status.md`); the page does not show that sentence. For CAISO, NYISO, ISO-NE and SPP the page says no public figure is held. A request-level queue would be needed; ERCOT publishes none.

7. **Will the power be there in a scarcity event?**
   The tool counts prices, not outages. In the last twelve months the price at `LZ_NORTH` was at or above USD 1,000 per MWh in 4 hours, all in January 2026, between 07:00 and 22:00 Central standard time; a flat 100 MW load paid USD 446,175 in them, of 29.55 million for the year. A load off in 100 hours a year under the rule was off in 3 of the 4 and avoided USD 306,942. The year 2021 shows the tail: 150.61 per MWh for the whole year. The page now sets ERCOT's own signal beside the price count: the hours in which its reserve adder averaged at least USD 100 per MWh. ERCOT published that adder until 4 December 2025 and no longer, so the count covers only 1,558 hours of the twelve months (1 October to 4 December 2025): 0 hours. Over the last year the adder was published (5 December 2024 to 4 December 2025): 1 hour, from 14:00 Central standard time on 30 June 2025, mean USD 412.74. The four hours at or above USD 1,000 are all in January 2026, after the adder ended, so no adder of this kind made them; since 5 December 2025 ERCOT prices scarcity through its real-time ancillary services, a report the warehouse does not hold. Whether a load would be curtailed: the tool does not know.

8. **How much does flexibility save, and would the rule work in practice?**
   Off in 100 hours a year: USD 31.46 per MWh against 33.73, a year's energy of USD 27.24 million against 29.55 million. Perfect foresight gives 29.72; the rule kept 57 percent of that saving. The breakeven: an hour off saves more than it gives up when a GPU-hour earns less than USD 0.4672 (USD 230.36 per MWh not bought). Limits: the rule spent its 100 hours by 5 July 2026 and had none left for August and September, two of the four dearest months of the 36; from 2015 to 2025 it kept 14 to 41 percent of the foreseen saving each year; the load is assumed to stop whole and at once. Shifting 20 percent of each day's energy reads 24.80 per MWh in real time.

9. **How clean is the power, and can I report it?**
   At ERCOT's monthly average the load's power carried 303.14 kg of CO2 per MWh, 265,548 tonnes a year for 100 MW, over 11 of the 12 months (the monthly table lacks one month of 2025). It is the grid's average for consumed electricity, not the marginal plant and not a claim about energy bought. The hourly figure depends on the window the live set holds, and the page prints that window's own first and last day. The method note's figures are of an older window (776 hours, 346.71 kg per MWh, when the live set held 35 days). Since session 245 the live set holds 430 days: on 13 October 2026 that was 10,144 hours for ERCOT, 9 August 2025 to 9 October 2026, and the same code gave 313.05 (flexible 312.31). Read the screen. By year the grid went from 414.04 kg per MWh in 2019 to 314.26 in 2025.

10. **Who checked these numbers, and what is still open?**
    Every hour of the default case equals the price tables to half a cent (103,055 hours). The page, its CSV and a Python mirror agree to the last decimal. `check-values` matched 477 of 477 values, then 471 of 477 on the final build, the six being the hourly carbon window above. Open: the Stata do-file has never been run; the whole test suite was not run in a clean copy; the delivery table's distribution rows, other riders and totals are new arithmetic of session 236 awaiting the owner's ruling; and the hurdle rate of 9.6 percent is a power plant builder's, not a datacenter's.

## 7. A five-minute demo, click by click

This path was written from the page's code and check scripts on the branch, not clicked through in a browser.

The page is in review. On the machine you will show it from, open the internal view first: `https://erw-flame.vercel.app/internal/unlock?token=<your internal token>` (or paste the token at `/internal/open`), then `/cost-of-power`. Session 260 read the path again against `main` at `34b468fa` and corrected step 1 of minute 2 to 3.

**Say this first:** this is what a 100 MW load paid for wholesale power at one Texas load zone over the last twelve months, hour by hour, from the grid's own prices; then what the model leaves out.

### Minute 0 to 1: "What will it pay?"

1. Open `/cost-of-power` with nothing after it. The panel "Your load" shows Grid ERCOT, Region `LZ_NORTH`, "Size, MW" 100, "How it runs" on "Flat: the same in every hour", "How it buys" on "Real time".
2. Read the sentence aloud: "A flat 100 MW load at LZ_NORTH in ERCOT, buying real time, paid USD 33.73 per MWh over the last twelve months, USD 29.55 million in all: USD 0.0684 per GPU-hour for power alone."
3. Name the three numbers under it: "Last twelve months, market energy" USD 33.73; "A bad month: the worst tenth of the last 36" USD 37.88 (August 2026); "Power per GPU-hour" USD 0.0684, with "100 MW powers 49,310 GPUs".
4. Point at the chart "Cost by year, USD per MWh, LZ_NORTH, real time". The tall bar is 2021: 150.61. The year 2025 reads 32.66.

### Minute 1 to 2: what is not in that number

1. Scroll to "What will it cost". The row "The hub beside it, HB_NORTH, a flat load" reads 32.51, with "the load zone is 1.22 per MWh above its hub".
2. Under it, "Delivery charges in Texas, USD per MWh". Read Oncor's column: Transmission 8.58, Distribution 0.48, Other riders -0.24, Total delivery 8.81. The other totals: CenterPoint 7.67, AEP Texas 8.39, Texas-New Mexico Power 7.10.
3. Say: these are never added to the 33.73. Read the one sentence under the table, which begins "Market energy at LZ_NORTH's real time price".
4. Say the cross-check from memory: Texas industrial customers paid USD 70.70 per MWh in July 2026 (EIA); this zone's energy that month was 30.59. The source line at the foot reads "Checked against: 6 published figures (EIA)."

### Minute 2 to 3: the other three questions

1. "Will the power be there?": "4 hours" at or above USD 1,000 per MWh, "January 2026 (4), between 07:00 and 22:00"; "A flat 100 MW load paid USD 446,175 in them." The table "The two counts" states the level and, for ERCOT, two rows of its own signal: the hours its reserve adder was at least USD 100 per MWh in the part of these months it was published (0, over 1,558 hours, 1 October to 4 December 2025), and the same adder over the last year it was published (1 hour, 5 December 2024 to 4 December 2025). Say that ERCOT ended this adder on 4 December 2025, so the January hours are not in it.
2. "How clean?": 303.14 kg of CO2 per MWh, 265,548 tonnes a year for 100 MW. For the third number, "Its own hours against the grid's average", read the screen: the repository holds 346.71 over 776 hours for the branch as built and 313.05 over 10,144 hours for the live set since session 245.
3. "How soon?": "Approved to energize" 8,927 MW and "Observed running, non-simultaneous peak" 3,900 MW by ERCOT's report of 19 June 2026; "137 requests, 140,000 MW" of new submissions. The sentence ends "No wait is estimated: ERCOT publishes none." "Rules in motion for a large load" read 8 on 13 October 2026.

### Minute 3 to 4: "Which option is better?", a flexible load

1. Scroll to "Scenarios A and B: two sites, or two contracts". Press **Scenario B**.
2. In "How the load runs" choose "Flexible: off in the 100 most expensive hours of each year". In "Upfront cost" type 50. The address gains `bw=1&bu=50&v=b`; no request is sent.
3. Read B's column: "Market energy, last twelve months" USD 31.46; "A year's energy" USD 27.24 million against A's 29.55 million; "Hours off, and the breakeven value of a GPU-hour" USD 0.4672, "off in 100 hours; USD 230.36 per MWh not bought".
4. Read the row "B against A": B's year is USD 2.3 million lower; B runs 4,930,966 fewer GPU-hours a year; B's present value is USD 15.16 million lower over 20 years at 9.6 percent; the two are equal when B's upfront cost is USD 201.60 per kW; B's USD 50 per kW returns 46.0 percent a year.
5. Scroll up once: "Will the power be there?" now adds that scenario B was off in 3 of the 4 hours and avoided USD 306,942, and "How clean?" adds B's 262,590 tonnes.

### Minute 4 to 5: two sites, then what matters most

1. With B in view press **Reset all of B**. In "Scenario B's site" choose the option that begins `TH_SP15_GEN-APND` under CAISO and press **Set B's site**. The page reloads and the address gains `bsite=caiso:TH_SP15_GEN-APND` (the address `/cost-of-power?bsite=caiso:TH_SP15_GEN-APND` opens the same comparison directly).
2. The table's heading names both sites. A reads USD 33.73 per MWh and B 28.58; "B against A" begins "A year's energy: USD 29.55 million in A, USD 24.97 million in B".
3. Each of the three answers adds one sentence for B's site. "Will the power be there?": 1 hour at or above the level, in which a flat 100 MW load paid USD 114,786. "How soon?": "CAISO publishes no figure of large load waiting or energized that the warehouse holds as a public table".
4. Say the caution of section 6, question 2: this is wholesale energy; the page holds no delivery figure for California.
5. Scroll to "What matters most". Each row moves one assumption by its step; the longest bar is first. At the defaults "Years counted" and "Hurdle rate" move nothing. The repository holds no pinned order of the bars: read the top row from the screen. "The chart as a table" under it holds the same figures.

**With a sixth minute, two contracts.** Press **Scenario A**, type 50 in "Contract share" and 30 in "Contract price" (the address gains `an=50&ac=30`). A's first row reads USD 31.86 per MWh against the market's 33.73, the headline's first number changes its label to "Last twelve months, energy with the contract", and the chart gains two rows.

### What the room asks

- **Are the prices real?** Yes: ERCOT's settlement point prices for the load zone, every 15 minutes, averaged to the hour. Nothing is filled.
- **Is the 33.73 a forecast?** No. It is the last twelve months, October 2025 to September 2026.
- **Why the zone and not the hub?** A Texas load settles at its load zone. The hub is shown beside it for reference.
- **Can I take the numbers away?** "Every month, CSV" and "The other tables, CSV" under the cost table; the default case hour by hour as "CSV", "Stata do-file" and "Python mirror" in the source line.

### If something goes wrong

- **"In review" instead of the tool:** the internal view is not open in this browser. Open the unlock address again.
- **"The live set could not be read":** the three answers read Supabase. The cost section and the scenarios still work; reload after a minute.
- **A number differs from this page:** the price files or the live set were rebuilt since 13 October 2026. The screen is the newer; each figure names its months.

## Where the numbers in this document come from

"Branch" is `origin/wip/236-datacenter` at `d4eaec68`. Since `aa3addbc` the branch's files are on `main`, and "(branch)" below reads "on `main`"; session 260 checked that each file named exists there.

| Number | Source file | Where in it |
|---|---|---|
| 33.73, 29.55 million, 876,000 MWh, 37.88, 0.0684, 49,310, 32.51, 1.22 | `docs/methods/datacenter_pays_algorithm.md` (branch) | "The default case"; sections 4.2 to 4.6 |
| Cost by year, 24.04 (2015) to 34.02 (2026) | the same | section 4.6 |
| 31.46, 2.27, 29.72, 4.01, 57 percent, 5 July, 24.80; k = 8, 684 of 720 | the same | sections 5.1 and 5.3 |
| 230.36, 0.4672, 258.57 million, 38.66, 27.24 million, 4,930,966, 15.16 million, 201.60, 46.0 percent, 31.86 | the same | sections 4.10 and 4.14 |
| 4 hours, 446,175, 306,942, 341,401 | the same; `archive/sessions/SESSION_228_REPORT.md` (branch) | section 4.15; "Read these first" |
| 303.14, 265,548, 11 of 12 months, 414.04, 314.26 | the same two | section 4.16; "Read these first" |
| 262,590 tonnes (flexible); 825 and 687 days; "approximately 220 days"; `LZ_WEST` 35.27, `HB_WEST` 30.66; 8 rules | `docs/brand/review-228/tables_default.csv.txt` (branch) | tables `carbon`, `waits_stated`, `regions`, `large_load` |
| 776 hours and 346.71 against 10,144 hours and 313.05 (312.31 flexible); "the last 35 days" | `archive/sessions/SESSION_248_REPORT.md` (main); `runs/session249/code_report_236.md` | "Correction to session 245's report"; "The live set moved during the session" |
| The two reworded sentences; 9 August 2025 to 9 October 2026 | `git show bba5d091`, `git show 805d88bb` (on `main` since `aa3addbc`) | `LoadAnswers.tsx`; `datacenter_pays_algorithm.md`, sections 4.15 and 4.16 |
| 430 days of hourly carbon | `docs/methods/emissions.md` (main) | "In the site's database" |
| 8,927, 3,900, 2,053, 137, 140,000 (the June report) | `archive/sessions/SESSION_228_REPORT.md` (branch); `docs/methods/ercot_large_load_status.md` (main) | "Read these first"; the table of reports |
| 9,042, 4,004, 2,168 (the March report) | `docs/methods/datacenter_pays_algorithm.md` (branch) | section 4.17 |
| The pause of 3 August 2026, 75 MW | `docs/methods/ercot_large_load_status.md` (main) | "Where the reports went after March 2026" |
| The 16 delivery figures (8.58, 0.48, -0.24, 8.81 and the rest) | `runs/session249/code_report_236.md`; `docs/brand/review-236/numbers_before_after.txt` (branch) | "Read these first"; the `dcd` keys |
| 6.260839, 5.956038; 41 lines, 3 conditional; 68.547301 and 75.527270, 7.83 and 8.62 | `docs/methods/datacenter_pays_algorithm.md` (branch); `site/data/datacenter/texas_delivery.json` (branch) | sections 4.6 and 4.18 |
| 28.58, 24.97 million; 114,786; 41 notices | `runs/session249/code_report_236.md` | "What was done", items 3 and 4; "To finish" |
| The six published comparisons (70.70, 251.10, 108.10, 23.97, 34.58, 78.55 and ours) | `docs/methods/datacenter_pays_algorithm.md` (branch) | "Cross-checks" |
| 103,055 hours, 412,220 rows, 0.00004, the do-file never run | the same | sections 3, 6 (item 17) and 8 |
| 477 of 477, 471 of 477, 57 of 57 | `runs/session249/code_report_236.md` | "Read these first"; "Checks, with exit codes" |
| 136.09 and 49.86 in 2021; 14 to 41 percent | `docs/methods/datacenter_cost.md` (main) | "What the rule kept" |
| 68.49 and 73.10 (New York City); 19 days; 289 of 744 | `docs/methods/datacenter_pays_algorithm.md` (branch) | section 6, item 3; "Cross-checks" |
| The adders' dates, 1 June 2014 to 4 December 2025 | `docs/methods/ercot_rt_price_adders.md` (main) | "What it is" |
| The adder count: USD 100; 1,558 hours, 0 at or above; 1 hour in the year to 4 December 2025, USD 412.74 | `docs/methods/datacenter_pays_algorithm.md`; `site/lib/datacenter/answers.ts`; `site/app/cost-of-power/LoadAnswers.tsx` | section 4.15, "ERCOT: its reserve adder"; `ADDER_USD`; the rows of "The two counts" |
| 4,249 of 4,249; 4,590 of 4,590; 119 of 119; 23 of 23 | `archive/sessions/SESSION_236_REPORT.md`; `archive/sessions/SESSION_237_REPORT.md` | "The landing" |
| Every default, bound and step of section 3 | `site/lib/datacenter.ts`, `site/lib/datacenter/finance.ts`, `answers.ts`, `delivery.ts`, `site/app/cost-of-power/model.ts` (branch) | `DEFAULTS`, `LIMITS`, `ASSUMED`, `SPECS`, `HURDLE`, `SCARCITY_USD`, `YEAR_HOURS` |
| Control labels and address parameters of section 7 | `LoadForm.tsx`, `LoadHeadline.tsx`, `LoadAnswers.tsx`, `LoadScenarios.tsx`, `LoadSiteB.tsx`, `page.tsx`, `site/components/decisions/ScenarioBlock.tsx` (branch) | the labels as written in the code |
| Load factor 0.9, 80 percent, 90 days ("Grid by grid") | `docs/methods/cost_of_power.md` (main) | "The calculator on `/cost-of-power`" |
