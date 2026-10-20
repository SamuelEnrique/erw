# Review pack: What a datacenter pays

- Address: `/cost-of-power`, the first tab of the cost of power, beside "What a generator earns" and "What a battery earns". A second view, "Grid by grid" (`?view=grids`), is an older model with its own method (`docs/methods/cost_of_power.md`) and shares no number with this pack.
- Status: in review, as every page is (`site/lib/release.ts`). A visitor sees the short "in review" page; the tool opens in the internal view only.
- Written by session 265 from `afacb21e` (branch `wip/265-datacenter-pack`) with that session's changes, on 2026-10-14. It replaces the how-it-works note of this tool in `docs/howitworks/` (sessions 249 and 260), whose content is folded in below.
- Figures are the default case as a local production build of that commit showed them on 2026-10-14 (price files built 2026-10-13T17:37:23Z; the live set read with the site's anon key). Prices and the live set are rebuilt daily: where the screen differs, the screen is the newer.

## 1. What it is for, and for whom

- For: a buyer of power for a large load (a datacenter developer, an AI company's energy lead), an investor testing a site's power cost, an operator asking what flexibility is worth.
- Four questions for a load the reader describes: what will it pay; will the power be there; how clean; how soon. Then two decisions: which option is better (scenarios A and B: two sites, two contracts or two ways of running) and what matters most (the sensitivity chart).
- What will it pay: wholesale energy at one hub or load zone, hour by hour, in USD per MWh, in USD for the size and per GPU-hour.
- Will the power be there: the hours of the last twelve months priced at or above USD 1,000 per MWh, what a flat load paid in them, and each grid's own signal where a table of it is held (ERCOT's reserve adder).
- How clean: the CO2 per MWh of the grid's consumed electricity, weighted by the load's own energy.
- How soon: the operator's own figures of large load approved and running, where a public table holds them; and, since session 265b, the figures public documents state on large loads in the grid (`large_load_public`): counts, the newest stated wait and the newest megawatt figure, each with its document's link. No wait is estimated.
- What it is not: a quote, a tariff calculator or a forecast. The headline is market energy alone: USD 33.73 per MWh at the default, where Texas industrial customers paid USD 70.70 in July 2026 by EIA's count (part 4).
- Grids: ERCOT, CAISO, NYISO, ISO-NE and SPP. MISO is listed and blank ("paused while terms are reviewed"); PJM is listed and blank ("licensed source needed").

## 2. The model, step by step

The default case: ERCOT, the North load zone (`LZ_NORTH`), a flat 100 MW load, bought in real time, 1.3 kW per GPU, an overhead ratio of 1.56.

1. The address is read into the load: `inputsFrom()` in `site/app/cost-of-power/model.ts` calls `inputsOf()` in `site/lib/datacenter.ts`; a number outside its bounds is brought inside them (`LIMITS`), and since session 265 the panel says so (`outsideOf()` in `site/app/cost-of-power/page.tsx`).
2. The price tables become the page's files: `warehouse/derived/datacenter_page.py` writes one file a grid and year under `site/data/datacenter/` (one price an hour; a real-time hour is the mean of its four 15-minute prices, held only when all four are, rounded to the cent). It makes no request.
3. A year's prices for the region and market: `expand()` in `site/lib/datacenter.ts`, one entry an hour of the grid's standard time all year (ERCOT and SPP UTC less 6 hours, CAISO less 8, NYISO and ISO-NE less 5); a missing hour stays null and is in no sum.
4. The load's shape: `weights()` in `site/lib/datacenter.ts` gives each hour a weight (1 flat; 0 when a flexible load is off; 0 to 2 for a load that shifts energy within the day). A flexible load follows the rule of `ruleThresholds()` and `ruleWeights()` (off when the day-ahead price, published the day before, is at or above the k-th dearest of the prior 30 days, until the year's budget of hours is spent); `monthsRuled()` runs it.
5. Months: `monthsOfYear()` and `monthsOf()` in `site/lib/datacenter.ts` sum price times weight (cost per MW) and the weights (energy); a month counts at 95 percent of its hours.
6. The last twelve months: `lastTwelve()` and `span()` in `site/lib/datacenter.ts`, the newest twelve counted months in a row. Cost over energy is the headline: 295,465.05 / 8,760 = USD 33.73 per MWh; times 100 MW, USD 29.55 million for 876,000 MWh.
7. A bad month: `last36()` and `badMonth()` in `site/lib/datacenter.ts`, the month at the top tenth of the 36 by nearest rank: August 2026, USD 37.88.
8. Per GPU-hour: `gpuHour()` in `site/lib/datacenter.ts`, price x kW per GPU x overhead ratio / 1,000: 33.7289 x 1.3 x 1.56 / 1,000 = USD 0.0684; `gpus()` gives 49,310 GPUs for 100 MW.
9. The hub beside the zone and every region's twelve months: `loadModel()` in `site/app/cost-of-power/model.ts` (`HB_NORTH` 32.51, the zone 1.22 above it).
10. Texas delivery charges, their own table: `deliveryOf()` and `deliveryStat()` in `site/lib/datacenter/delivery.ts` turn 41 tariff lines of four wires utilities into USD per MWh for a flat load; `conditionOf()` (session 265) marks a line billed per kVA or per meter, and a line the tariff applies only to some loads. Never added to the market cost.
11. Will the power be there: `scarcity()` and `adders()` in `site/lib/datacenter/answers.ts`, read by `readAnswers()` from the live set: 4 hours at or above USD 1,000 per MWh, all in January 2026; USD 446,175 for 100 MW; ERCOT's reserve adder at or above USD 100 in 0 of the 1,558 hours it was published in these months. Since session 280, `byGrid()` in the same file reads `scarcity_hours_by_grid` for ERCOT and CAISO and sets two counts side by side at the grid's hub (`ByGridCounts` in `site/app/cost-of-power/LoadAnswers.tsx`): ERCOT's `HB_HUBAVG` was at or above USD 1,000 in 1 of the 8,760 hours held, and its reserve adder was above zero in 44 of the 1,558 hours held (1 October to 4 December 2025); CAISO's `TH_SP15_GEN-APND` in 1 of 8,735, its own signal (an EEA or a flex alert) in 0 of 8,760. A grid the table does not hold keeps the lines above.
12. How clean: `l12Carbon()`, `windowCarbon()` and `yearlyCarbon()` in `site/lib/datacenter/answers.ts`: 303.14 kg CO2 per MWh at the monthly average, 265,548 tonnes a year for 100 MW; 313.01 over the 10,160 hours held hour by hour.
13. How soon: `largeLoad()` in `site/lib/datacenter/answers.ts` reads `ercot_large_load_status` (ERCOT only): 8,927 MW approved to energize and 3,900 MW observed running by the report of 19 June 2026; the rules in motion from `site/data/datacenter/rules.json`. Since session 265b, `largeLoadStatements()` in `site/lib/largeloadpublic.ts` reads `large_load_public` for the grid and `statedOf()` in `site/lib/datacenter/statements.ts` counts it (ERCOT: 67 figures, 55 of megawatts and 12 of a wait, from 5 entities in 28 documents); `StatedLine` in `site/app/cost-of-power/LoadAnswers.tsx` writes one paragraph, never a sum. Since session 280, `listsOf()` in `site/lib/datacenter/statements.ts` and `StatedList` beside it list every row, each with its date, its figure and its document's link, no quoted text: ERCOT's 43 as the operator, 24 of utilities and the Commission, and, for a grid in one state (`GRID_STATE`: Texas, California, New York), the 24 of other grids in that state (El Paso Electric, 21; American Electric Power, 3). Each figure has its own check key, `dcll|<the row's grid>|row:<statement_id>:mw` or `:wait`; a wait written with words before its number stands as written, with no key.
14. Scenario B at a site of its own: `siteBOf()` in `site/app/cost-of-power/model.ts` (`bsite=<grid>:<region>`); steps 3 to 8 and 11 to 13 run again for that site.
15. The scenarios, in the browser: `parseScenarios()`, `resultOf()`, `presentValue()`, `levelPrice()` and `against()` in `site/lib/datacenter/finance.ts` turn the year into a present value at the cost of capital, a fixed price with the same present value and an all-in cost per GPU-hour. Nothing is sent.
16. What matters most: `sensitivity()` in `site/lib/datacenter/finance.ts` moves each assumption one step down and up and sorts the bars by the larger move.

So a price becomes a dollar per MWh this way: four 15-minute prices become an hour; hours times the load's weights become a month; twelve counted months become the headline. Nothing else is added on the way.

## 3. Every assumption

"Fixed" in the default column means the reader cannot change it. Address names are the query-string parameters.

| Assumption | Default | Source | Ruling of 12 October |
|---|---|---|---|
| Grid (`grid`) | ERCOT | ERW's choice: the first grid of `ORDER` in `site/lib/datacenter.ts` | none |
| Region (`region`) | the grid's main region: `LZ_NORTH`, `TH_SP15_GEN-APND`, `N.Y.C.`, `.H.INTERNAL_HUB`, `SPPNORTH_HUB` | the owner's ruling of session 140: a Texas load settles at its load zone; `docs/methods/datacenter_cost.md` | none |
| Size (`mw`) | 100 MW, bounds 0.1 to 10,000 | ERW's choice; every USD and MWh figure is the per-MW figure times the size | none |
| How it runs (`run`) | flat | ERW's choice | none |
| Hours off a year (`n`) | 100, bounds 0 to 8,784 | ERW's choice (`DEFAULTS` in `site/lib/datacenter.ts`) | none |
| Share of hours off (`pct`) | 5 percent | ERW's choice | none |
| Share of a day's energy shifted (`shift`) | 20 percent, bounds 0 to 50 | ERW's choice | none |
| How it buys (`buy`) | real time; day-ahead when real time holds no twelve counted months | ERW's choice | none |
| Power per GPU (`ag`, `bg`) | 1.3 kW, bounds 0.05 to 20 | NVIDIA DGX H100 datasheet: 8 GPUs, 10.2 kW maximum system power | none |
| Facility overhead ratio, PUE (`ap`, `bp`) | 1.56, bounds 1 to 3 | Uptime Institute, Global Data Center Survey 2024; Google reports 1.09 for its fleet | none |
| Delivery and other charges (`ad`, `bd`) | USD 0 per MWh, bounds 0 to 500 | ERW's choice: the headline is market energy alone | none |
| Change of prices (`ae`, `be`) | 0 percent a year, bounds -20 to 20 | none held: no cited forecast | none |
| Upfront cost (`au`, `bu`) | USD 0 per kW, bounds 0 to 20,000 | none held | none |
| Years counted (`al`, `bl`) | 20, bounds 1 to 40 | none held | none |
| Cost of capital: a generator's WACC, Lazard (`ah`, `bh`) | 9.6 percent, bounds 0 to 40, editable | Lazard, Levelized Cost of Energy+, June 2025: "60% debt at an 8% interest rate and 40% equity at a 12% cost", 0.6 x 8 + 0.4 x 12 | none on 12 October; the owner's ruling of 11 October (session 196) set 9.6; label of 14 October (session 265) |
| Debt coverage | none: the page models no debt | not applicable; the generator's and battery's 1.25 is "ERW's choice" on those pages | none |
| Contract share (`an`, `bn`) | 0 percent | ERW's choice: fully merchant | the chain prompt of 12 October: "compare two sites or two contracts" |
| Contract price (`ac`, `bc`) | USD 0 per MWh, bounds 0 to 1,000 | the reader's own term; no published price held | the same |
| Scenario B's site (`bsite`) | A's own site | session 236, `SITE_B` in `site/lib/datacenter/finance.ts` | the same |
| A month counts | at 95 percent of its hours | ERW's choice (`NEAR = 0.95`) | none |
| Standard time | no daylight saving shift | ERW's choice: every day has 24 hours | none |
| A real-time hour | the mean of four 15-minute prices, all four needed, to the cent | ERW's rule; over 103,055 hours rounding moves the mean by USD 0.00004 | none |
| The rule's memory and threshold | the prior 30 days; k = 8 for 100 hours a year | `PRIOR_DAYS`, `ruleThresholds` in `site/lib/datacenter.ts` | none |
| The rule's budget | the hours named, each calendar year | the owner's ruling of 7 October 2026 | none |
| The scarcity level | USD 1,000 per MWh, every grid | FERC Order 831's offer cap; `SCARCITY_USD` in `site/lib/datacenter/answers.ts` | "keep USD 1,000 for every grid ... and add each grid's own signal as a second count when its table is held (ERCOT's adders first)" (review of 12 October, section F) |
| ERCOT's own signal | the reserve adder's hourly mean at or above USD 100, where published (to 4 December 2025) | `ADDER_USD` in `answers.ts`; `ercot_rtm_price_adders` | the same section F |
| Carbon basis | consumed electricity, the balancing authority's average | `carbon_intensity_monthly`, `carbon_intensity_hourly`; `docs/methods/emissions.md` | the live set holds at least 13 months hour by hour (ruling of 12 October, `emissions.md`) |
| Large load | the latest ERCOT report; the change from one a year or more before | `largeLoad` in `answers.ts`; `ercot_large_load_status` | none |
| Large-load statements | the grid's rows of `large_load_public`: counts, the newest wait as written and the newest megawatt figure, each with its link; not added | `statedOf` in `site/lib/datacenter/statements.ts`; session 272's helper | the owner's ruling of 14 October 2026 (session 272): public, "facts with a link, no quoted text" |
| Delivery: hours in a year | 8,760, a leap year too | `YEAR_HOURS` in `site/lib/datacenter/delivery.ts` | none |
| Delivery: a flat load's demand in the four peaks and its billing demand | its size | by construction, from the reader's load | none |
| Delivery: a kVA | not converted in the total without conditions; counted as a kW (power factor 1) in the total with them | session 265, the owner's list of 14 October ("no added assumption"); session 236 decision 4 | the chain prompt of 12 October: "one row per component with its USD per MWh and the total; the tariff lines go to the CSV" |
| Delivery: meters | a rate per meter or per ESI ID is conditional; one meter in the total with conditions | the same | the same |
| Delivery: a line the tariff applies only to some loads | in neither total; named under the table (3 of 41 lines) | the tariff's own words (`applies` in `texas_delivery.json`) | the same |
| Delivery: service voltage | transmission voltage | the rate class a large load takes (`texas_delivery_charges`) | the same |
| The Commission's wholesale rate | rate x 1,000 / 8,760, its own row, not a line of a retail tariff | Public Utility Commission of Texas, Docket 57491 (2025, approved) and 59080 (2026, filed) | none |

## 4. The cross-checks

"Gap" is ours less theirs. A gap is not an error to close: the reason says what each side measures. Every published figure is one a methods note of the repository quotes with its source; none was read tonight.

| What is compared | Ours | Theirs | Gap | Reason |
|---|---|---|---|---|
| `LZ_NORTH` real time, July 2026, against Texas industrial customers (EIA, Electric Power Monthly, Table 5.6.A) | USD 30.59 per MWh | 70.70 | -40.11 | Ours is wholesale energy at one zone; EIA's is everything an industrial customer paid: supply, delivery, demand and other charges |
| `LZ_NORTH` real time, July 2025, against Texas industrial customers, July 2025 (the same table, as the methods note quotes it: 6.61 cents per kWh) | 34.18 | 66.10 | -31.92 | The same; ours computed tonight from the page's hourly CSV (744 hours) |
| SP15 real time, July 2026, against California industrial customers (the same table) | 39.47 | 251.10 | -211.63 | The same, in a state whose delivery and public-purpose charges are several times the energy |
| NYISO New York City, day-ahead, July 2026, against New York industrial customers (the same table) | 77.45 | 108.10 | -30.65 | The same; EIA's is the whole state; day-ahead because July's real-time hours are held in part (289 of 744) |
| SP15 day-ahead peak block, January to September 2026, against ICE's "SP15 EZ Gen DA LMP Peak" (EIA's file of ICE prices) | 24.04 over 166 delivery periods | 23.97 | +0.07 | A traded expectation against the cleared price |
| NP15, the same block, against ICE's "NP15 EZ Gen DA LMP Peak" | 34.35 over 73 periods | 34.58 | -0.23 | The same; NP15 trades on fewer days |
| New England internal hub, day-ahead peak, against ICE's "Nepool MH DA LMP Peak" | 77.72 over 157 days | 78.55 | -0.83 | The same; January's cold days traded above where the market cleared |
| A flat load in CAISO, 2025, real time: the mean of SP15 and NP15 against Berkeley Lab's flat profile at all CAISO nodes (Land-Based Wind Energy Technology Update 2026, quoted in `generator_earns_algorithm.md`) | 34.23 (SP15 31.19, NP15 37.27, the page's library over 8,735 hours each) | 34.21 | +0.02 | Two hubs against every node; the equal weight on the two hubs is ours |
| Oncor's transmission factor as printed (6.260839 USD per 4CP kW a month) against the table's transmission row | 8.58 | 6.260839 x 12,000 / 8,760 = 8.58 | 0 | The table converts the tariff's own figure for a flat load and adds nothing |
| The Commission's wholesale transmission rate, 2025 (USD 68.547301 per kW a year, Docket 57491) against Oncor's transmission row | 8.58 | 7.83 per MWh for a flat load | +0.75 | A utility's factor recovers the Commission's rate and the utility's own wholesale costs; the rate alone is the smaller |
| The cost of capital's default against Lazard's stated financing | 9.6 percent | 0.6 x 8 + 0.4 x 12 = 9.6 | 0 | A generator's weighted cost, not a datacenter owner's: no datacenter's is held |
| Power per GPU against NVIDIA's DGX H100 datasheet (10.2 kW for 8 GPUs) | 1.3 kW | 1.275 kW | +0.025 | Rounded up to one decimal; the server's share is in it |
| Overhead ratio against Uptime Institute's survey average (2024) and Google's fleet | 1.56 | 1.56; Google 1.09 | 0; +0.47 against Google | The industry average, not a large operator's |
| ERCOT, the page's twelve months: hours at or above USD 1,000 at the load zone (the page's own price files) against the hub (`scarcity_hours_by_grid`, session 280) | 4 (`LZ_NORTH`) | 1 (`HB_HUBAVG`) | +3 | A zone against the hub average; and the page counts an hour only when all four of its 15-minute prices are held, the table the mean of the intervals held |
| ERCOT's own signal: the page's count of the adder at or above USD 100 against the table's count above zero, the same 1,558 hours | 0 | 44 | -44 | The level: most hours above zero are fractions of a cent (`docs/methods/scarcity_hours_by_grid.md`, which reports the same 44) |
| CAISO, SP15, the page's twelve months: the page's count against the table's | 1 | 1 | 0 | The same hub; the hour starting 05:00 UTC on 27 August 2026 |
| "How soon?", ERCOT: the paragraph's count of figures against the rows the list shows | 67 | 43 + 24 = 67 | 0 | The same read; the 24 rows elsewhere in Texas are listed apart and in no count |
| The page against its replication CSV and the Python mirror (tonight) | 33.73; 37.88; 0.0684; 32.51; 4 hours, USD 446,175; 303.14; 313.01 over 10,160 hours | the same | 0 | Part 8 |

- Not compared: a price from a datacenter's own filing or press release (none is held); ERCOT's hubs and zones against ICE (EIA's 2026 file holds no ERCOT hub); a datacenter owner's cost of capital (none is held); a market monitor's average load price for ERCOT (no figure of Potomac Economics' reports is quoted in the repository for a load: "not held").

## 5. The edge cases tested

Tested tonight on a local production build of this commit (port 3265, the internal view), read by `runs/session265/edges.mjs`; the HTML of each is kept in `runs/session265/edges/`.

| Case | What was typed (the address) | What the page does |
|---|---|---|
| 1 MW | `/cost-of-power?mw=1` | USD 33.73 per MWh, USD 295,465 in all, USD 0.0684 per GPU-hour. Delivery rises where a rate per account is spread over less energy: Oncor 9.60, AEP Texas 10.14 (8.81 and 8.39 at 100 MW) |
| 1,000 MW | `/cost-of-power?mw=1000` | USD 33.73, USD 295.47 million; delivery Oncor 8.80, AEP Texas 8.37 |
| Flexible, 0 hours | `/cost-of-power?run=hours&n=0` | The flat figure: USD 33.73, "USD 0.00 per MWh less than a flat load (USD 0.00 if perfectly foreseen)" |
| Flexible, 8,760 hours | `/cost-of-power?run=hours&n=8760` | The rule's threshold falls to the cheapest prior price, so the load runs only in the cheapest hours: off in 8,713 hours, USD -4.55 per MWh, USD -21,370 in all, USD -0.0092 per GPU-hour; "How clean?" 1,409 tonnes a year. No error; a negative price is a price. For the owner (part 9, question 5) |
| A region with no carbon data | `/cost-of-power?grid=spp` | No grid of the page lacks carbon whole; SPP lacks most: "7 of the twelve months have no intensity in the table and are left out": 432.46 kg per MWh over 5 months, 378,834 tonnes. The wording was "has ... is" before session 265 |
| A grid not held | `/cost-of-power?grid=miso`, `/cost-of-power?grid=pjm` | ERCOT is shown, and since session 265 the panel says: "Grid: "miso" is not held here, so ERCOT is shown." |
| A region not held | `/cost-of-power?grid=ercot&region=LZ_NOWHERE` | `LZ_NORTH` is shown with the line "Region: "LZ_NOWHERE" is not held for this grid, so LZ_NORTH is shown." |
| Size outside its range | `/cost-of-power?mw=20000`; `/cost-of-power?mw=0` | 10,000 MW and 0.1 MW are used, and the panel says "Size: 20000 is outside 0.1 to 10000 MW, so 10000 is used." (session 265: the guard was there, the line was not) |
| Size not a number | `/cost-of-power?mw=abc` | 100 MW, with "Size: "abc" is not a number, so the default is used." |
| Hours outside their range | `/cost-of-power?run=hours&n=9000` | 8,784 is used, with the line; the figures are those of 8,760 |
| A scenario's assumption outside its range | `/cost-of-power?ah=50`; `/cost-of-power?bu=-5` | 40 and 0 are used, with "Scenario A, Cost of capital: a generator's WACC, Lazard: 50 is outside 0 to 40 percent a year, so 40 is used." |

- Not tested tonight: a value typed into a scenario's field in the browser (the shared `NumberField` in `site/components/decisions/ScenarioBlock.tsx` brings it inside its bounds and shows the typed text while the field has focus; no line says so). The shared component is the battery's too, so it was left for the owner (part 9).

## 6. What the model cannot see, ranked

1. Everything on the bill that is not wholesale energy. Size: USD 40.11 per MWh in Texas in July 2026, 211.63 in California, 30.65 in New York (part 4). The tool itemizes one part, for Texas only: delivery of USD 8.81 (Oncor) and 8.39 (AEP Texas) with no condition, 7.10 to 8.81 with the conditional lines. A retailer's margin, hedging, ancillary services, uplift, taxes: no number held.
2. Future prices. Since session 352 (20 October 2026) the reader chooses the price years in "Your load" (read from `price_years_by_window`): the last twelve months (the default), any calendar year held, the three- and seven-year averages, or every month held; scenario A and B and the results follow, the flexible way and scenario B at its own site from their own rows, at the run's defaults. Size: a flat load at `LZ_NORTH` paid USD 21.68 (2016) to 150.61 (2021) by calendar year, against 33.73 over the last twelve months; a line under the results names the cheapest and the dearest whole year. No forecast is held.
3. The tariff or contract a large load negotiates: shape, settlement point, collateral, term, minimum demand, exit terms. No number held.
4. ERCOT's four coincident peaks. A flat load's demand in them is its size; the transmission component at stake is USD 6.92 to 8.58 per MWh by utility. What a load off in those intervals saves: no number held.
5. Capacity charges outside ERCOT (NYISO, ISO-NE). None is added; `iso_all_capacity_prices` is internal and not read. No number held.
6. Basis from the hub or zone to the load's node. Hub to zone: `LZ_NORTH` is USD 1.22 above `HB_NORTH`. Session 358 (`node_basis_daily`, `node_basis_summary`): over 1 October 2025 to 30 September 2026 (day-ahead, 335 days) the eight load zones' mean basis to `HB_HUBAVG` ran from 0.07 (`LZ_SOUTH`) to 4.78 (`LZ_CPS`), `LZ_NORTH` 0.98; across every resource node (786 points) the 10th percentile was -5.63, the median 0.18, the 90th 5.38. A load in ERCOT settles at its load zone; the nodes are where generators and storage settle, so a node's basis applies to a load only behind a generator's point. No load's own node is held.
7. What flexibility a real load can deliver: it turns off whole, at once, with no minimum. Modeled saving USD 2.27 per MWh under the rule, 4.01 foreseen, for 100 hours a year.
8. The interconnection wait: no wait is estimated for any grid. Since session 265b the page shows the newest wait a public document states (ERCOT: 60 days, expected, the Public Utility Commission of Texas, 18 September 2026; CAISO: 60 to 90 days, the California ISO), a single statement and not a measured wait. It moves the year a figure starts, not the figure.
9. Behind-the-meter supply: not modeled. No number held.
10. Curtailment and physical shortage: the scarce-hour count is a count of prices; ERCOT's adder ended on 4 December 2025. Whether a load would be shed: no number held.
11. Marginal carbon: the figure is the grid's average for consumed electricity. The window alone moved the hourly figure from 346.71 (776 hours) to 313.01 (10,160 hours).
12. Stale or thin history: New York's real time lacks 19 days of July 2026, so its window is July 2025 to June 2026; ERCOT's load zones stop at 3 October 2026 until the data machine refreshes them.

## 7. The ten hardest questions

### 1. Is USD 33.73 per MWh what my datacenter would pay?
No. It is what a flat 100 MW load paid for wholesale energy at `LZ_NORTH` in real time, October 2025 to September 2026, unhedged. Texas industrial customers paid USD 70.70 in July 2026 (EIA); the tool's figure for that month is 30.59. In Oncor's area the page states delivery of USD 8.81 in its own table. The rest of the gap the tool does not know.

### 2. Scenario B in California shows USD 28.58 against Texas's 33.73. Is California cheaper?
For wholesale energy at SP15 over its own twelve months, yes: USD 24.97 million a year for 100 MW against 29.55 million. For a delivered bill, no number on the page says so, and EIA says the opposite: USD 251.10 per MWh for California industry in July 2026 against 39.47 at SP15. California's delivery reads "not held yet".

### 3. What will power cost over the twenty years you discount?
The tool does not know. It repeats the last twelve months, changed by the rate typed (default 0: no cited forecast). By year at this zone: 24.04 (2015), 21.68, 23.88, 30.82, 36.35, 21.82, 150.61 (2021), 62.93, 48.69, 26.41, 32.66 (2025), 34.02 for nine months of 2026.

### 4. Why do two of the four Texas utilities show "conditional" where a total should be?
CenterPoint and Texas-New Mexico Power bill per kVA and per meter. A kVA is a kW only at a power factor of 1, and the count of a site's meters is not in the tariff, so by the owner's rule of 14 October no total is stated without those two figures. With them (power factor 1, one meter) the totals are 7.67 and 7.09 (7.10 until session 307 counted TNMP's rider DCRF once), in the row below, labelled conditional. Oncor (8.81) and AEP Texas (8.39) bill per kW, per kWh and per retail customer, and need neither.

### 5. Can I cut the transmission charge by being off in the four coincident peaks?
Not computed. A flat load's four-peak demand is its size: Oncor's transmission is USD 8.58 per MWh (6.260839 x 12,000 / 8,760), AEP Texas's 8.16. The tool would need each year's four intervals and the load's draw in them. Texas-New Mexico Power's factor (sheet of 1 September 2025) is probably superseded.

### 6. Where are capacity and ancillary charges?
Not in any figure. ERCOT has no capacity market and prices scarcity inside energy. In NYISO and ISO-NE a capacity cost reaches load and the tool adds none. The reader can type a figure under "Delivery and other charges".

### 7. Will the power be there in a scarcity event?
The tool counts prices, not outages: 4 hours at or above USD 1,000 per MWh, all in January 2026, between 07:00 and 22:00 Central standard time; a flat 100 MW load paid USD 446,175 in them. ERCOT's adder counted 0 hours at or above USD 100 in the 1,558 hours it was published in these months, and 1 hour in its last published year. Session 254's table `scarcity_hours_by_grid` would give each grid's own count, but the live set does not hold it tonight (read with the anon key: 0 rows), so the page keeps today's count.

### 8. How long until a new large load is energized?
The tool does not know and estimates no wait. ERCOT's report of 19 June 2026: 8,927 MW approved to energize, 3,900 MW observed running, the approved figure up 2,053 MW since 28 May 2025; 137 new submissions, about 140,000 MW, by 13 March 2026. Since session 265b the page adds what public documents state (`large_load_public`, public by the owner's ruling of 14 October 2026, landed by session 272): for ERCOT 67 figures from 5 entities in 28 documents, the newest wait 60 days (expected, the Public Utility Commission of Texas, 18 September 2026), the newest megawatt figure 22,000 MW (ERCOT, 17 September 2026); for CAISO 48 figures, NYISO 5, SPP 19, ISO-NE none. Each with its document's link; never added. None is a measured wait.

### 9. How clean is the power, and can I report it?
303.14 kg CO2 per MWh at ERCOT's monthly average, 265,548 tonnes a year for 100 MW, over 11 of the 12 months; 313.01 over the 10,160 hours held hour by hour (9 August 2025 to 10 October 2026). It is the grid's average for consumed electricity, not the marginal plant and not a claim about energy bought. By year: 414.04 (2019) to 314.26 (2025).

### 10. Who checked these numbers, and what is still open?
Tonight: `check-values` 682 of 682 on the cost-of-power pages, twice; the Python mirror equals the page value by value (part 8). Open: the Stata do-file has never been run; the hurdle rate is a generator's, not a datacenter's; the delivery table's conditional rows await the owner's reading of "no added assumption" (part 9).

## 8. What Samuel's Stata run must reproduce

The files: `site/public/datacenter/erw_2026_datacenter_hourly.csv` (exported 2026-10-11T17:27:06Z), `erw_2026_datacenter_carbon.csv` (rewritten by session 265 from the live set at 2026-10-14, so its hourly window is the page's, 10,160 hours), `erw_2026_datacenter_replication.do` and `.py`. Their defaults are the page's: 100 MW, 1.3 kW per GPU, an overhead ratio of 1.56, the level USD 1,000. The `.py` was run tonight (`runs/session265/replication_py3.out`, exit 0).

| Name | The page shows | The .py printed tonight | The do-file's display line |
|---|---|---|---|
| The last twelve months | Oct 2025 to Sep 2026 | 2025-10 to 2026-09 | `display "the last twelve months: " ...` |
| Market energy, a flat load, USD per MWh | 33.73 | 33.73 | `display "market energy, a flat load, last twelve months, USD per MWh: " %9.2f s_l12_usd_mwh` |
| Cost for 100 MW | USD 29.55 million | 29,546,505 | `display "cost for 100 MW, USD: " ...` |
| Energy for 100 MW | 876,000 MWh | 876,000 | `display "energy for 100 MW, MWh: " ...` |
| Power per GPU-hour | USD 0.0684 | 0.0684 | `display "power per GPU-hour, USD: " %9.4f ...` |
| GPUs that 100 MW powers | 49,310 | 49,310 | `display "GPUs that 100 MW powers: " ...` |
| The hub beside it | 32.51 | 32.51 | `display "the hub beside it, a flat load, USD per MWh: " ...` |
| Zone less hub | 1.22 | 1.22 | `display "the load zone less its hub, USD per MWh: " ...` |
| A bad month | August 2026, 37.88; USD 2.82 million | 2026-08, 37.88; 2,818,474 | `display "a bad month, nearest rank " ...` |
| Cost by year | 2021: 150.61; 2025: 32.66 | the same | the loop's `display "year ...: months that count ..."` |
| Hours at or above USD 1,000 | 4 | 4 | `display "hours of the last twelve months at or above USD 1000 per MWh: " r(N)` |
| What a flat load paid in them | USD 446,175 | 446,175 | `display "what a flat load of 100 MW paid in them, USD: " ...` |
| Carbon, monthly average | 303.14 kg per MWh | 303.14 | `display "this load's carbon, last twelve months at the grid's monthly average, kg CO2 per MWh: " ...` |
| Tonnes a year | 265,548 | 265,548 | `display "tonnes of CO2 a year for 100 MW: " ...` |
| Hourly window | 10,160 hours, 313.01 | 10,160, 313.01 | `display "a flat load's own hours over them, kg CO2 per MWh (the grid's mean): " r(mean)` |

```
cd "C:\Users\lossa\Documents\erw\site\public\datacenter"
do erw_2026_datacenter_replication.do
```

- The Python mirror, for comparison: `python erw_2026_datacenter_replication.py` in the same folder. The scenarios (present value, cost of capital) and the delivery table are not in the replication files: they are the browser's (`finance.ts`) and the delivery library's, held by `tests/test_session236.py` and `tests/test_session265.py`.

## 9. Questions only Samuel can answer

1. The delivery table's reading of "no added assumption" (session 265's). (a) As built: a line billed per kVA or per meter is conditional, the first total states only lines with no condition (Oncor 8.81, AEP Texas 8.39; CenterPoint and Texas-New Mexico Power "conditional"), the second total counts them at a power factor of 1 and one meter. (b) Drop the second total: two columns of four show no total. (c) Ask the reader for a power factor and a count of meters: two fields, the panel grows.
2. Texas-New Mexico Power's distribution recovery factor is in the file twice, once "per Meter" and once "per ESI ID", USD 635.58 each (sheet 141, 29 December 2025). (a) Keep both, as the tariff lists both. (b) Count one: the conditional total falls by USD 0.0087 per MWh at 100 MW (0.87 at 1 MW). (c) Read the sheet again on the data machine.
3. Each delivery figure names its tariff lines, with schedule, page, date and document, on hover (session 265), and the three lines the tariffs apply only to some loads are named under the table. (a) Keep. (b) Lines in the CSV only, as the 12 October prompt said ("the tariff lines go to the CSV"). (c) A row a line: the table grows to 41 rows.
4. `scarcity_hours_by_grid` is not in the live set tonight. (a) The data machine loads it (it is in `live_set.yaml` under review hold) and a later session reads it into "Will the power be there?". (b) Keep the page's own count and the adder rows. (c) Read only CAISO's notices from it.
5. A flexible load at 8,760 hours a year runs only in the cheapest hours and shows a negative price (USD -4.55 per MWh). (a) Keep: it is the rule's arithmetic. (b) Cap the hours a year at a share (say 8,000) with the line saying so. (c) Add one line under the headline when the load runs in under a tenth of the hours.
6. `large_load_public` on "How soon?" (ruled public on 14 October; the page reads it since session 265b): (a) as built, one paragraph: counts, the newest wait and the newest megawatt figure, each with its link; (b) also scenario B's grid (its line still says only the operator's report); (c) a table of the grid's rows by stage, which would be a new block.
7. The cost of capital is a generator's WACC. (a) Keep Lazard's 9.6 with the new label. (b) A datacenter owner's cost of capital, if you name a source. (c) Two defaults, one per scenario.
8. A value typed into a scenario field outside its range is brought inside it with no line (shared component). (a) Add the line to the shared `NumberField` (moves no figure; the battery page is checked unchanged). (b) Leave it: the address line covers links.

## Appendix: the five-minute demo

Written from the page's code and check scripts, not clicked through. Open the internal view first: `https://erw-flame.vercel.app/internal/open`, then `/cost-of-power`.

- Minute 0 to 1, "What will it pay?": the panel "Your load" shows ERCOT, `LZ_NORTH`, 100 MW, flat, real time. Read the sentence: "A flat 100 MW load at LZ_NORTH in ERCOT, buying real time, paid USD 33.73 per MWh over the last twelve months, USD 29.55 million in all: USD 0.0684 per GPU-hour for power alone." Under it: USD 37.88 (August 2026) and 49,310 GPUs. The chart's tall bar is 2021, 150.61.
- Minute 1 to 2, what is not in that number: "The hub beside it, HB_NORTH" 32.51; the Commission's rate row, 7.83 (2025, approved), "not a line of a retail tariff"; "Delivery charges in Texas, as the tariffs state them": Oncor 8.58, 0.48, -0.24, total 8.81; CenterPoint and Texas-New Mexico Power "conditional", 7.67 and 7.10 at a power factor of 1 and one meter. Never added to the 33.73. Then EIA's 70.70 for July 2026 against 30.59.
- Minute 2 to 3, the other three questions: 4 hours at or above USD 1,000, USD 446,175; the adder rows (0 hours over 1,558; 1 hour in its last year). 303.14 kg per MWh, 265,548 tonnes. 8,927 MW approved and 3,900 MW running (19 June 2026); "No wait is estimated: ERCOT publishes none."
- Minute 3 to 4, a flexible load: Scenario B, "Flexible", upfront 50: USD 31.46 per MWh, USD 27.24 million against 29.55 million; breakeven GPU-hour USD 0.4672.
- Minute 4 to 5, two sites, then what matters most: B's site `TH_SP15_GEN-APND` (`/cost-of-power?bsite=caiso:TH_SP15_GEN-APND`): 28.58 against 33.73. In "What matters most" the longest bar at the defaults is "Delivery and other charges" (USD 0.0101 per GPU-hour for USD 5 per MWh); "Years counted" and the cost of capital move nothing at a price change of 0.
- What the room asks: the prices are ERCOT's settlement point prices, 15-minute, averaged to the hour, nothing filled; 33.73 is not a forecast; a Texas load settles at its zone; the downloads are "Every month, CSV", "The other tables, CSV" and the hourly CSV with its do-file and mirror.

## Where every number comes from

| Number | File | Section |
|---|---|---|
| 33.73, 29.55 million, 876,000, 37.88, 0.0684, 49,310, 32.51, 1.22, 4 hours, 446,175, 303.14, 265,548, 313.01, 10,160 hours, 8,927, 3,900, 2,053, 137, 140,000 | the local build of tonight, `runs/session265/edges/default.html`; `docs/methods/datacenter_pays_algorithm.md` | sections 4.2 to 4.17 |
| 295,465.05 over 8,760 hours; the price files' date | `site/data/datacenter/index.json`, `ercot_2025.json`, `ercot_2026.json` | `built`; `regions.LZ_NORTH.rt` |
| Cost by year, 24.04 (2015) to 34.02 (2026) | `runs/session265/replication_py3.out`; `datacenter_pays_algorithm.md` | section 4.6 |
| 31.46, 2.27, 4.01, 27.24 million, 0.4672, 28.58, 24.97 million | `docs/methods/datacenter_pays_algorithm.md`; the old note (sessions 249 and 260) | sections 4.10, 4.14, 5.1 |
| The delivery figures (8.58, 0.48, -0.24, 8.81; 7.67; 8.39; 7.09; 1 MW and 1,000 MW) | `site/lib/datacenter/delivery.ts` on `site/data/datacenter/texas_delivery.json`; `runs/session265/edges_c1.out` | `deliveryOf`, `deliveryStat` |
| 6.260839, 5.956038, 68.547301, 7.83, 8.62, 41 lines, 3 conditional, 635.58 | `site/data/datacenter/texas_delivery.json`; `datacenter_pays_algorithm.md` | `rows`, `matrix`; sections 4.11 and 4.18 |
| 70.70, 66.10, 251.10, 108.10, 30.59, 39.47, 77.45, 23.97, 24.04, 34.58, 34.35, 78.55, 77.72 | `docs/methods/datacenter_pays_algorithm.md` | "Cross-checks" |
| 34.18 (July 2025) | `site/public/datacenter/erw_2026_datacenter_hourly.csv` | the 744 hours of `std_month` 2025-07 |
| 31.19, 37.27, 34.21 | `site/data/datacenter/caiso_2025.json` with `flatMean()`; `docs/methods/generator_earns_algorithm.md` | the CAISO cross-checks |
| 9.6, 1.3, 10.2 kW, 1.56, 1.09 | `site/lib/datacenter/finance.ts`, `site/lib/datacenter.ts` | `SPECS.hurdle`, `ASSUMED` |
| USD 1,000, USD 100, 1,558 hours, 0 and 1 hour, 4 December 2025 | `site/lib/datacenter/answers.ts`; `docs/methods/scarcity_hours_by_grid.md`; `docs/methods/ercot_rt_price_adders.md` | `SCARCITY_USD`, `ADDER_USD`; "What the first run holds" |
| 0 rows of `scarcity_hours_by_grid` and `large_load_public` | the live set read with the anon key, 2026-10-14 08:31 UTC | `runs/session265/` (this session's notes) |
| 341 rows of `large_load_public` after session 272 (ERCOT 67, CAISO 48, NYISO 5, SPP 19, ISO-NE 0); 5 entities, 28 documents, 12 waits, 55 megawatt rows for ERCOT; 60 days; 22,000 MW | the live set read with the anon key, 2026-10-14 10:27 UTC, through `statedOf()` | `site/lib/datacenter/statements.ts` |
| 341 statements, 67 entities | `archive/sessions/SESSION_255_REPORT.md` | "Read these first" |
| Edge-case figures (-4.55, -21,370, 8,713 hours, 432.46, 378,834, 7 of 12 months, 295,465, 295.47 million) | `runs/session265/edges_c1.out`, `runs/session265/edges/` | the case's line |
| 682 of 682 | `runs/session265/cv1_c1.out`, `cv2_c1.out` | the last line |
| 346.71 over 776 hours | `docs/methods/datacenter_pays_algorithm.md`; the carbon CSV before session 265 | section 4.16 |
| 136.09 and 49.86 in 2021; 14 to 41 percent | `docs/methods/datacenter_cost.md` | "What the rule kept" |
