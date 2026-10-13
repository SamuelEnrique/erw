# How it works: What a generator earns

Address: `/cost-of-power/seller`, the second of the three cost-of-power tabs. The page is in review (`site/lib/release.ts`): a visitor sees the in-review page, and so does anyone whose browser has not opened the internal view.
Written on 2026-10-13 by session 249 from the branch `origin/wip/235-generator`, commit `c7ce17de` (session 235), and checked again the same day by session 260 against `main` at `34b468fa`. The page landed as `aa3addbc` (09:14 UTC on 13 October 2026, sessions 235 and 236 together). Between `c7ce17de` and `34b468fa` no file of the page's code changed (`site/app/cost-of-power/seller/`, `site/lib/seller/`, `site/lib/merchant.ts`: `git diff` is empty). What did change: the methods note gained section 12, CAISO at ERCOT's depth (session 253), and the data machine's daily run rebuilt the capture file and the file of the battery beside the plant.
Every figure below is for the default case unless it says otherwise: ERCOT, solar, 100 MW, the hub average (`HB_HUBAVG`), real-time prices, October 2025 to September 2026, on the model's snapshot built 2026-10-04. The capture file on `main` was built 2026-10-13T17:38:04Z; session 260 recomputed the default case's price received from it and it is unchanged: 23.27 against 32.17, over 8,736 hours and 80,832,584 MWh.

## 1. What it is for, and for whom

- **The question.** What did a solar plant, a wind plant, a battery or a gas peaker earn selling every MWh at a hub's price, year by year; what price did it receive against the hub's plain average; does that cover its debt; and is it worth building, with or without a contract.
- **For whom.** The method note says the page is "built for a lender's reading: the bad months, the stress days, and debt service coverage" (`docs/methods/cost_of_power.md`, "The seller's side"). Since session 186 the page also holds what a developer or an investor asks for: two scenarios of costs and financing, NPV and IRR to equity, and since session 235 the PPA price at which NPV is zero.
- **Where.** Five grids: ERCOT, CAISO, NYISO, ISO-NE and SPP. 39 hubs and zones (ERCOT 14, CAISO 3, NYISO 11, ISO-NE 9, SPP 2). MISO is blank ("paused while terms are reviewed"). PJM is blank ("licensed source needed"). An address that names either opens ERCOT.
- **What it is not.** It is merchant by default: no contract, no capacity payment, no ancillary service, no tax credit. It is a grid's whole fleet at a hub's price, not one site at its node. The method note's own words: "It is not a forecast and not a valuation."
- **The default answer, in one line.** 100 MW of ERCOT solar earned USD 59.85 per kW in the last twelve months, was paid USD 23.27 per MWh against a hub average of USD 32.17, covered its debt 0.67 times, and has an NPV of USD -74.16 million at a hurdle rate of 12 percent.

## 2. The model, in numbered steps

Everything is computed per 1 MW of nameplate and multiplied by the reader's MW at the end. Every result is linear in MW.

1. **The price comes in.** The tool reads the hub's real-time price. An hour is the mean of its four 15-minute prices and exists only when all four are held. An hour with a missing interval has no price and is in no figure. A hub that holds no twelve months of real time is priced day-ahead, and the page says which.
2. **The shape comes in (solar, wind).** For each hour the tool takes the grid's whole solar or wind generation from EIA-930 and divides it by the fuel's installed nameplate in that balancing authority in that month, from EIA-860M. The result is MWh per MW installed: a fleet's shape, not a site's.
3. **An hour becomes dollars.** Revenue in an hour is output per MW times the hour's price. A solar or wind plant sells in every hour, also at a price below zero. Nothing is curtailed.
4. **A battery's day.** For each local day whose every hour holds a price, the tool solves the best schedule exactly, knowing the whole day's prices in advance: round trip 86 percent, from empty each day, at most one full cycle. It is energy only and an upper bound.
5. **A peaker's hour.** The peaker runs in each hour whose price is strictly above Henry Hub times the heat rate plus variable O&M, and earns the difference. No start cost, no minimum run, no outage.
6. **Hours become a month.** A month's revenue, energy, capture price (sales over energy), flat price (the mean price of the same hours) and capture rate are the sums over its hours. A month is held when the asset used at least 90 percent of its hours (a battery: 90 percent of its days). A month under 90 percent is in no figure.
7. **Months become the headline.** The last twelve months are the newest held month and the eleven before it, all held. Revenue per kW is their sum over 1,000: USD 59,852.26 per MW, so 59.85. The long-run averages are over the last three full calendar years (102.24) and every full year held (130.80, 2019 to 2025).
8. **The price received.** A second builder weighs each hour's price by the fleet's generation itself: `sum(price x generation) / sum(generation)`, against `sum(price) / hours` over the same hours. Here a month counts at 95 percent of its hours. Default: 23.27 against 32.17, USD 8.90 (27.7 percent) below, over 8,736 hours and 80,832,584 MWh of fleet generation.
9. **Another hub.** Choosing another hub or zone runs steps 1 to 7 again with that hub's own price and the same fleet shape. Two hubs of one grid differ by their prices only.
10. **Costs.** Fixed O&M for a year is `fom x 1,000 x MW`: USD 1,250,000. The annual debt payment is `capex x 1,000 x MW x share x r / (1 - (1 + r)^-n)`: 1,375 x 1,000 x 100 x 0.60 is USD 82,500,000 of debt, the factor at 8 percent over 35 years is 0.0858033, and the payment is USD 7,078,769.
11. **Coverage.** Debt coverage is revenue less fixed O&M, over the debt payment: (5,985,226 - 1,250,000) / 7,078,769 = 0.67 times.
12. **Finance.** The tool repeats the last twelve months' revenue in every year of the project's life, cut each year by the degradation rate. Equity pays `capex x (1 - share)` in year 0 (USD 550 per kW) and receives revenue less fixed O&M less the debt payment each year. NPV discounts those flows at the hurdle rate; IRR is the rate at which NPV is zero, found by bisection.
13. **Two contract prices.** The price at which coverage reaches 1.25 times is `(1.25 x debt + fom) / E`: (1.25 x 70.79 + 12.5) / 2.580 = USD 39.14 per MWh. The breakeven PPA price is the price at which NPV is zero for a contract on the whole plant over the debt's years: USD 58.36 per MWh. A battery and a peaker get a toll in USD per kW-month instead.
14. **What matters most.** Each assumption is moved down and up by one stated step, the others held, and NPV is computed again. The rows are sorted by the larger move.
15. **The bad months and the stress days.** The held months are sorted by revenue: the median month, the 10th-percentile month and the worst three are real months, not interpolated. For ERCOT the tool sums revenue over the days of Winter Storm Uri, Winter Storm Elliott and the summer 2023 heat against a normal week. Since session 212 these are in the two CSV downloads, not on the page face; the worst month stays as a row of the results.
16. **A battery beside it (solar and wind, ERCOT and CAISO).** The plant and a battery behind one interconnection are solved together, one day at a time, against the main hub's day-ahead prices. The result is one row of the results table.

**Not read by the model:** `ercot_rtm_price_adders` (session 244, on main, `docs/methods/ercot_rt_price_adders.md`). ERCOT's scarcity adders are already inside the hub price the model reads (`docs/methods/capacity_and_ancillary.md`: ERCOT's scarcity pricing "is inside the energy price already"), so scarcity revenue is counted. It is not shown apart, and the tool cannot say how much of a year's revenue was scarcity.

## 3. Every assumption, its default and its source

"Your plant" is the panel at the left. "Assumptions" is the panel under "Is it worth building?"; each field there has its own Reset and an address parameter (`a` or `b`, then the letter shown).

### Prices, shapes and rules of the model

| Assumption | Default | Where the user changes it | Source |
|---|---|---|---|
| Grid | ERCOT | "Grid" (`iso`) | ERW's choice: the only grid held from July 2018; the other four from September 2024 |
| Hub or zone | the grid's main hub: hub average, SP15, New York City zone, Internal hub, North hub | "Hub or zone" (`hub`) | The price board's main hubs, `docs/methods/cost_of_power.md` |
| Asset | Solar | "Asset" (`asset`) | ERW's choice |
| Size | 100 MW; a battery 100 MW / 400 MWh | "Size, MW" (`mw`, 1 to 5,000); "Energy, MWh" (`mwh`, 1 to 8 times the MW) | `DEFAULT_SIZE`, `site/lib/merchant.ts`; Lazard's storage cases are 100 MW |
| Market | real time; day-ahead where a hub holds no twelve months of real time | fixed (follows the hub) | ERW's rule, methods note 4.3 and section 5 |
| An hour's price | the mean of four 15-minute prices, only when all four are held | fixed | ERW's rule, methods note 3.1 |
| First month | July 2018 (ERCOT); September 2024 (the other four) | fixed | EIA-930's generation by fuel begins 2018-07-01 (`SHAPE_START`, `warehouse/derived/merchant_revenue.py`) |
| Solar and wind output | the grid's whole fleet by hour over installed nameplate that month | fixed; "Your plant's own year" takes the reader's own 8,760 hourly values | EIA-930 (`Adjusted SUN Gen`, `Adjusted WND Gen`) and EIA-860M |
| Output above nameplate, or below zero | kept as EIA reports it (ERCOT: 1,428 solar hours above nameplate; CAISO: 4,197 solar hours below zero) | fixed | ERW's choice: nothing is trimmed; counted in `tables.csv` |
| California's hours | read one hour earlier from 2023-11-01 to 2025-12-02 | fixed | `docs/methods/eia930_caiso_break.md` |
| Curtailment, negative prices | none: the plant sells every hour | fixed | By construction, methods note 3.2 |
| A month is held | 90 percent of its hours (a battery: of its days) | fixed | ERW's rule (`NEAR = 0.9`) |
| A month counts for the price received | 95 percent of its hours | fixed | ERW's rule (`NEAR = 0.95`, `warehouse/derived/capture_price.py`) |
| Battery round trip | 86 percent | fixed | Lazard LCOS v10.0, the low end of 92 to 86 percent |
| Battery cycles, start | at most one full cycle a day, each day from empty | fixed | The battery page's rule |
| Battery foresight | the day's prices are all known in advance | fixed | By construction: an upper bound |
| Battery duration priced | 4 hours; 2 hours when MWh over MW is 3 or less; a longer battery is priced as 4 hours | "Energy, MWh" | Lazard prices two durations (`durationOf`); methods note section 6, item 12 |
| Peaker heat rate | 10.725 MMBtu per MWh | "Heat rate, MMBtu per MWh" (`hr`, 6 to 16) | Lazard, gas peaking new build, midpoint of 10,275 to 11,175 Btu per kWh |
| Peaker variable O&M | USD 4.25 per MWh | "Variable O&M, USD per MWh" (`vom`, 0 to 50) | The same, midpoint of 3.50 to 5.00 |
| Gas price | Henry Hub spot of the local day, the last trading day's on a day without one; no basis | fixed | EIA, `eia_fuel_spot_prices` |
| Peaker run rule | runs when the price is strictly above fuel plus variable O&M; no start cost, minimum run, ramp or outage | fixed | By construction, methods note 3.4 |
| Battery beside the plant | the plant's MW, 4 hours, perfect foresight | "A battery beside it": "Battery size, MW" (`bmw`), "Duration" (`dur`: 2, 4, 8), "Perfect foresight" or "Day-ahead schedule" (`strat`) | ERW's choice; the strategy moves only the second row of `tables.csv` |
| The pair's limit | the plant's capacity, or its highest hour of the twelve months when higher (107.495 MW for 100 MW) | fixed | `docs/methods/cost_of_power.md`, "Session 162" |
| The pair's prices | the main hub's day-ahead price, whatever hub is chosen; no discharge in an hour priced below zero | fixed | The same |

### Costs and financing (the ten assumptions of a scenario)

| Assumption | Default | Where the user changes it | Source |
|---|---|---|---|
| Capital cost, USD per kW | solar 1,375; wind 2,100; battery 610 (2 hours), 1,110 (4 hours); peaker 1,300 | "Capital cost" (`c`, 0 to 10,000) | Lazard, Levelized Cost of Energy+, June 2025, midpoints of 1,150 to 1,600; 1,900 to 2,300; 340 to 880; 620 to 1,600; 1,150 to 1,450 |
| Debt share, percent | 60, every asset | "Debt share" (`s`, 0 to 100) | Lazard: "60% debt at an 8% interest rate". The battery page uses 20 since session 208; this page's battery stays at 60 |
| Interest rate, percent a year | 8 | "Interest rate" (`r`, 0 to 30) | The same |
| Term of the debt, years | the asset's life: 35; 30; 20; 30 | "Term of the debt" (`t`, 1 to 40, whole) | Lazard: "Economic life sets debt amortization schedule". A term longer than the life is cut to the life |
| Fixed O&M, USD per kW a year | 12.5; 32.25; 11.2 and 22; 13.5 | "Fixed O&M" (`f`, 0 to 500) | Lazard, midpoints of 11.00 to 14.00; 24.50 to 40.00; 3.0 to 8.2 and 3.0 to 8.0 per kWh times the hours; 10.00 to 17.00 |
| Degradation, percent a year | 0 (solar, wind, peaker); 2.6 (battery) | "Degradation" (`d`, 0 to 20) | Battery: Lazard LCOS v10.0. The others: no cited rate is held, and the page says so |
| Project life, years | 35; 30; 20; 30 | "Project life" (`l`, 1 to 40, whole) | Lazard's life of each asset |
| Hurdle rate, percent a year | 12 | "Hurdle rate" (`h`, 0 to 40) | Lazard: "40% equity at a 12% cost". The owner's ruling of 2026-10-12 (session 208); it was 9.6 from session 196 to 207 |
| Contract share, percent | 0: fully merchant | "Contract share" (`n`, 0 to 100) | No contract. Solar and wind: a share of the energy. Battery and peaker: a share of the capacity |
| Contract price | 0 | "Contract price" (`p`, 0 to 1,000); "Make B a PPA" fills B's breakeven | The reader's own term: "no published price is held" |

### Constants the reader cannot change

| Assumption | Default | Where the user changes it | Source |
|---|---|---|---|
| Annual debt payment, 100 MW | solar USD 7,078,769; wind 11,192,257; battery 3,727,791 (2 hours), 6,783,357 (4 hours); peaker 6,928,540 | fixed (computed from the four fields above) | Level payments, `debtUsd` in `site/lib/seller/finance.ts` |
| Revenue in every future year | the last twelve months, repeated, less degradation | fixed | ERW's choice: "An assumption, not a forecast" (methods note 11.3) |
| Coverage target | 1.25 times (`TARGET`) | fixed | ERW's choice: the code and the note cite no source for 1.25 |
| Contract length | the debt's years; the price is paid flat; after them the whole plant is in the market | fixed ("Term of the debt" shortens it) | ERW's choice, session 212; for Samuel's ruling in the session 235 report |
| Breakeven PPA share | the scenario's own contract share, or 100 percent when it holds none | fixed | `ppaShare`, session 235 |
| "Make B a PPA" | share 100, price B's breakeven rounded up to the cent | one button | `asPpa`, session 235 |
| IRR search | bisection from -99 to 1,000 percent a year; "none" when NPV has one sign at both ends | fixed | ERW's choice (`IRR_LOW`, `IRR_HIGH`) |
| Sensitivity steps | capital cost USD 100 per kW; debt share 10 points; interest 1 point; term 5 years; fixed O&M USD 5; degradation 1 point; life 5 years; hurdle 1 point; contract share 10 points; contract price USD 1 | fixed | ERW's choice (`swing` in `SPECS`) |
| Tax, tax credit, inflation, repowering, residual value | none | fixed | By construction, methods note 11.3 and 11.6 |

**Two files disagree.** The table in section 11.1 of the methods note still gives the hurdle rate's default as 9.6. The code (`HURDLE = 12`), the note's own opening paragraph and the check scripts say 12. The code is newer (session 208); session 212's report lists the stale row.

## 4. The cross-checks

"Gap" is ours less theirs. The first ten rows are the published figures the page's source line counts ("Checked against: 10 published figures"), read on 2026-10-11. None of them is a real plant's revenue.

| What is compared | Ours | Theirs | Gap | Reason | Where it is written |
|---|---|---|---|---|---|
| ERCOT solar, contract price for coverage of 1.25 | USD 39.14 per MWh | Lazard LCOE, utility solar, unsubsidized: USD 38 to 78 | +1.14 to -38.86: inside the range, at its low end | Ours covers debt 1.25 times and fixed O&M and nothing else; Lazard's also returns 12 percent on equity and pays taxes | Methods note, "Cross-checks" |
| ERCOT wind, the same | USD 56.85 per MWh | Lazard LCOE, onshore wind: USD 37 to 86 | +19.85 to -29.15: inside | The same, over 3,028 MWh a year per MW | The same |
| Gas peaker, toll for coverage of 1.25 | USD 8.34 per kW-month | Lazard LCOE, gas peaking: USD 149 to 251 per MWh | not stated | Not one unit: a fixed charge against a cost per MWh | The same |
| Capital cost, solar | USD 1,375 per kW | Annual Technology Baseline (ATB) 2025: USD 1,490 per kW AC in 2024 | -115, 7.7 percent | Lazard's midpoint against one modeled 100 MW tracking plant | The same |
| Capital cost, wind | USD 2,100 per kW | ATB 2025: USD 1,968, the 2023 market average | +132, 6.7 percent | A 2025 midpoint against a 2023 average | The same |
| Fixed O&M, solar | USD 12.50 per kW a year | ATB 2025: USD 24.66 | -12.16 | The ATB adds land, property and administration | The same |
| Fixed O&M, wind | USD 32.25 per kW a year | ATB 2025: USD 43 | -10.75 | The ATB counts every operating cost as fixed | The same |
| Degradation, solar | none | ATB 2025: 0.7 percent a year | -0.7 | No cited default for solar; for Samuel's ruling | The same |
| SP15 day-ahead peak block, January to September 2026 | USD 24.04 per MWh (NP15: 34.35) | ICE index in EIA's file: 23.97 (NP15: 34.58) | +0.07 (NP15: -0.23) | A traded expectation against the cleared price | The same |
| New England hub day-ahead peak block, same months | USD 77.72 per MWh | ICE index: 78.55 | -0.83 | The same; January -7.41 | The same |
| Not compared | any ERCOT hub price | EIA's 2026 file holds no ERCOT hub | no number held | No public index for the default case's own hub | The same, last line |
| The default case rebuilt from one hourly CSV | 59.85; 102.24; 130.80; 23.27; 32.17; 7,078,769; 0.67 | the page | largest 0.0000006 USD per MWh | Rounding of month sums. The Stata do-file "has never been run" | Methods note, section 8 |
| The model at each main hub by a second builder | 99 ERCOT months | the snapshot | equal; the peaker's September 2026 differs 0.19 percent | Henry Hub prices that arrived after the snapshot | Methods note, 5.1 |
| The flat price, model against capture file | 3,708 hub-months | each other | within USD 0.0001 per MWh | One price, two builders | Methods note, 5.1 |
| The two capture prices | 23.20 (model) | 23.27 (capture file) | under 1 percent in 40 of 42 cases; SPP South solar 4.7 percent | Two sets of weights; a fleet that grows in the span | Methods note, 5.1 and 9.1 |
| The finance library against the battery page's | 400 seeded cases | `lib/battery/finance.ts` | 0 | The same arithmetic | `site/scripts/test-seller-finance.mjs` |
| The debt formula on Lazard's wind illustration | USD 30.4 million a year | Lazard: 300 MW at 1,900 USD per kW, 342 million of debt | equal | Lazard's own financing | `docs/methods/cost_of_power.md` |
| One solar month by hand, ERCOT 2025-07 | 277.9898 MWh per MW; USD 7,941.5254 per MW | the table | equal | Recomputed from the source files | `tests/test_session51.py` |
| The pair's solver against a second solver | the page's simplex | scipy's HiGHS | one part in ten billion | Two implementations | `site/scripts/test-hybrid.mjs` |

**California, checked at ERCOT's depth (session 253; the methods note's section 12).** The page counts 20 published figures where it counted 10: the ten more are the rows of that section that hold a gap, five of them below (session 257, as committed on its branch at `9e0bbfe8`; it holds once that branch is on `main`). Ours is the page's own model for CAISO in 2025 at real-time prices; "theirs" was read on 13 October 2026.

| What is compared | Ours | Theirs | Gap | Reason | Where it is written |
|---|---|---|---|---|---|
| A gas peaker at SP15, margin over fuel, USD per kW | 30.05, running 34.0 percent of the hours | 0.78 net, running 1.32 percent: the market monitor's new combustion turbine | +29.27 | The page's rule has no cost of carbon: California's allowance on the fuel alone takes ours to 6.95. Their unit also pays to start and runs at least an hour | Methods note, 12.5 |
| The same at NP15 | 41.47, running 42.0 percent | 3.52 net, running 3.43 percent | +37.95 | The same; with the allowance ours is 10.11 | The same |
| Wind, the price the fleet's shape received, USD per MWh | 30.29 at SP15, 35.53 at NP15; their mean 32.91 | 32.97: Berkeley Lab's wind profile at all power plants; 30.82 at the wind plants' own nodes after curtailment | -0.06 against the profile | The model sees the profile at a hub, not the plants' nodes or curtailment, which take a further 2.15 in their figures | The same |
| Solar, capture rate | 45.8 percent at SP15, 71.7 at NP15 (2025) | 25.1 percent (Berkeley Lab, 2024, energy only) | not computed: no year is held by both | CAISO's prices are held from September 2024; their newest solar year is 2024 | The same |
| Solar, breakeven PPA price | USD 72.58 per MWh on 2,075 MWh per MW | USD 47.06: LevelTen's CAISO solar index, 2024 | +25.52 | Ours has no tax credit and returns 12 percent to equity on a whole fleet's output | The same |
| Wind, breakeven PPA price | USD 79.50 per MWh on 2025's 3,125 MWh per MW | USD 78.2: LevelTen's CAISO wind index, 2025 | +1.30 | The same | The same |
| The page's CAISO files against a rebuild from the tables | 26 months at each of SP15, NP15 and ZP26 | the rebuild | equal in every whole month | October 2026 is under way; the peaker's September 2026 at SP15 differs by late Henry Hub prices | Methods note, 12.1 |

**The checks, as the reports state them.** On the branch (session 235): `check-values` 179 of 179 values on this page; `check-seller-scenarios.mjs` 106 of 106. At the landing: the whole suite on a clean copy, 3,728 tests OK; `check-values` on every page, 4,249 of 4,249; `check-seller-scenarios` exit 0. Not clean: `check-seller.mjs` still exits 1 on 12 of 33, because it describes the page before session 212 (session 241c's report, "To finish").

## 5. What it cannot see, ranked by how much it moves the answer

Ranked by the held number where there is one. Where the repository holds no number the place in the list is the ERW's judgment, and the line says "no number held".

1. **Future prices: which year is repeated.** The finance repeats October 2025 to September 2026, USD 59.85 per kW, for 35 years. The three-year average is 102.24 and the seven-year average 130.80. Single years run from 59.46 (2024) to 217.53 (2021, Winter Storm Uri). The NPV at any revenue but the last twelve months': no number held, and the page has no field for it.
2. **PPA and hedge terms.** The default is fully merchant. The plant received USD 23.27 per MWh; it needs 39.14 for coverage of 1.25 and 58.36 for an NPV of zero. A contract here is a share at a flat price for the debt's years: no shape, no settlement point, no credit, no negative-price clause. What PPAs sign at: no number held.
3. **Tax credits and taxes.** None is modeled. Size of the effect: no number held. Lazard's range in the cross-check is its unsubsidized one.
4. **Scarcity and availability.** For 100 MW of solar the 18 days of Uri earned USD 12,382,220, against USD 5,985,226 for the whole of the last twelve months. The model assumes the plant ran through the storm: no outage, no frozen equipment. ERCOT's on-line reserve adder averaged USD 7.05 per MWh in 2021 and 0.07 in 2025 to 4 December (`ercot_rtm_price_adders`); the model does not read that table.
5. **Basis between hub and node, and congestion.** The plant is paid the hub's price. Basis at a node: no number held, and the warehouse holds no node price for a plant. The nearest held figure is hub to hub: ERCOT solar earned 47.51 at the West hub and 72.48 in the Houston load zone, against 59.85 at the hub average; coverage 0.49 to 0.85.
6. **Capital cost and fixed O&M off the midpoint.** These are fields, not blind spots, but the defaults are contested. USD 100 per kW of capital cost moves NPV by USD 8.21 million; USD 5 of fixed O&M by 4.09 million. The Annual Technology Baseline's fixed O&M for solar is 12.16 above the default.
7. **Ancillary services and capacity revenue.** ERCOT has no capacity market, so nothing is missing there for solar and wind. For a battery it is large: energy alone is USD 58.53 per kW here, against 81.40 on What a battery earns, 33 percent of it from ancillary services. NYISO and ISO-NE pay for capacity apart; those prices are in an internal table the page does not read: no number held.
8. **Degradation.** Solar's default is none; the Annual Technology Baseline 2025 gives 0.7 percent a year. One point a year moves NPV by USD 3.51 million.
9. **A fleet, not a site.** Resource, trackers, age and location are averaged over the grid. Site against fleet: no number held. EIA-860M lists some plants late, so the shape passes 1.0 in 1,428 ERCOT solar hours, which lifts it.
10. **Curtailment and negative prices.** EIA-930's generation excludes curtailed energy, so the fleet's own curtailment is already out of the shape. One site's curtailment order is not. In an hour priced below zero the plant still sells. Size: no number held.
11. **Real time against day-ahead.** The same 100 MW at the same hub earned USD 6,328,531 at day-ahead prices (364 days) and 5,985,226 in real time. A row priced day-ahead is not comparable with one priced in real time.
12. **Perfect foresight (battery) and perfect hourly information (peaker).** Both are upper bounds. On the battery page the day-ahead schedule gives 73.00 against 81.40 with foresight. For this page's energy-only battery: no number held.
13. **The peaker's start costs and delivered gas.** No start cost, no minimum run. Gas is Henry Hub; in New York and New England delivered gas costs more in winter, so the margin there is overstated. Size: no number held.
14. **California's carbon allowance on a peaker's fuel.** The peaker's rule is fuel plus variable O&M on every grid. In California a gas plant also buys allowances: at SP15 in 2025 the page's rule gives USD 30.05 per kW, the same rule with the allowance 6.95, and the market monitor's own unit earned 0.78. Every CAISO peaker figure on the page is too high by that. Solar and wind are not touched. Session 257 left the rule as it is: adding the allowance waits for a ruling.
15. **California's wind since May 2026.** EIA-860M lists 3,650 MW of New Mexico wind in CAISO's balancing authority from May 2026, so the shape's denominator grew: the last twelve months hold 2,477 MWh per MW against 3,125 in 2025. Whether EIA-930's generation counts that plant was not checked. For California's wind, 2025 is the cleaner year.
16. **Age of the files.** The model's snapshot (`site/data/merchant_snapshot.json`) was built by hand on 2026-10-04 and no schedule rebuilds it; its newest held month is September 2026. The capture file and the file of the battery beside the plant are rebuilt by the data machine's daily run.

## 6. The ten hardest questions

1. **"Your NPV is USD -74.16 million. Are you saying solar in Texas is not worth building?"**
   No. It says that 100 MW selling every MWh at the hub average, with no contract and no tax credit, repeating the last twelve months for 35 years, does not return 12 percent to equity. Revenue less fixed O&M was 59.85 - 12.50 per kW against a debt payment of 70.79: coverage 0.67 times. IRR reads "none": no rate from -99 to 1,000 percent sets NPV to zero. The method note says the block "does not say which to choose".

2. **"Is this my plant at my node?"**
   No. It is ERCOT's whole solar fleet by the hour, scaled to 100 MW, paid the hub's price. The basis at a node: the tool does not know. It would need the plant's own settlement point prices, which the warehouse does not hold. "Your plant's own year" takes a pasted year of hourly output, but still prices it at the main hub, day-ahead.

3. **"Why the last twelve months? It is your worst case."**
   It is the newest year, not a chosen one: USD 59.85 per kW. The page shows the other two beside it: 102.24 for 2023 to 2025 and 130.80 for 2019 to 2025. The newest two calendar years are 59.46 (2024) and 63.54 (2025); the three before them are 217.53, 197.43 and 183.72. The finance reads only the last twelve months. The NPV on a long-run average: no number held; it needs a revenue field the page does not have.

4. **"Where is the tax credit?"**
   Nowhere. The flows have "no tax, no tax credit, no repowering, no residual value, no inflation". The size of the effect: the tool does not know. It would need the credit's value and the project's eligibility as scenario assumptions.

5. **"What PPA price does it need, and what are PPAs signing at?"**
   USD 58.36 per MWh for an NPV of zero, on the whole plant for 35 years. USD 39.14 keeps coverage at 1.25 times. The market paid 23.27. Lazard's unsubsidized cost of utility solar is USD 38 to 78. What PPAs sign at: no published contract price is held, and the page says so beside the button.

6. **"How much of the good years was Uri and scarcity, and will it come back?"**
   2021 earned USD 217.53 per kW; the 18 days of Uri alone earned USD 12,382,220 for 100 MW, with a best day of USD 4,060,021 on 2021-02-17. The capture rate that year was 55 percent. Hours in which ERCOT's on-line reserve adder averaged at least USD 100 per MWh: 70 in 2021, 103 in 2022, 18 in 2023, 4 in 2024 and 1 in 2025. The model does not read that table, so it cannot split a year's revenue into scarcity and the rest. Whether it comes back: the tool makes no forecast.

7. **"What about curtailment and negative prices?"**
   The fleet's curtailed energy is already missing from EIA's generation. A site's own curtailment is not modeled, and the plant sells at negative prices. Size for a site: the tool does not know; it would need the site's curtailment record. The page links to the curtailment page's free-energy section for the hub chosen.

8. **"Where are capacity and ancillary revenue?"**
   Not counted. In ERCOT there is no capacity payment to count. In NYISO and ISO-NE there is, and the tool leaves it out: no number held. For a battery, use What a battery earns: energy alone is 58.53 per kW here against 81.40 there.

9. **"A battery with perfect foresight: is that honest?"**
   It is labeled an upper bound, and it is one. The battery page's own cross-check sets its foresight figure of USD 148 per kW in 2024 beside a published fleet average of USD 55 (Modo Energy, quoted in the battery note's cross-checks). On this page the battery is energy only at 60 percent debt; its toll for coverage of 1.25 is USD 8.90 per kW-month (session 186's report). Its NPV at 12 percent: no number held (USD -79.57 million at 9.6, session 196).

10. **"Who has checked this, and how old is it?"**
    Twenty published figures stand beside it, ten of them California's (session 257), and the default case can be rebuilt from one hourly CSV to the cent. No ERCOT hub price is compared, because no public index holds one. No real plant's settlement is compared. The Stata do-file has never been run. The snapshot is from 2026-10-04, built by hand; nothing rebuilds it on a schedule.

## 7. A five-minute demo, click by click

This path was written from the page's code and check scripts, not clicked through in a browser. The page is in review. Session 260 read the path again against `main` at `34b468fa`: the page's code is the code it was written from.

Open the internal view first: `https://erw-flame.vercel.app/internal/unlock?token=<your internal token>`, or `/internal/open`, paste the token and press **Open the internal view**. Then open `/cost-of-power/seller`.

**Say this first:** this is what Texas's solar fleet was paid, hour by hour, at the hub's real price; then what that does to a lender's coverage and an owner's return.

### Minute 0 to 1: what did it earn?

1. The address is bare. In **Your plant**: Grid **ERCOT**, Hub or zone **Hub average (HB_HUBAVG)**, Asset **Solar**, Size, MW **100**.
2. Read the sentence under **What did it earn?**: "Over the last twelve months, Oct 2025 to Sep 2026, a merchant solar plant in ERCOT priced at the hub average earned USD 59.85 per kW. The long-run average of 2023 to 2025 was USD 102.24 a year, and of the 7 full years held (2019 to 2025) USD 130.80."
3. Name the three headline numbers:
   - **Revenue, last twelve months**: 59.85 USD/kW.
   - **Price received at the hub average**: 23.27 USD/MWh, "-8.90 USD per MWh (-27.7 percent) against the flat average of 32.17".
   - **Debt coverage, last twelve months**: 0.67 times, on debt payments of USD 7.08 million a year.

### Minute 1 to 2: the years, and the price received

1. The chart **Revenue by year, USD per kW**. The methods note holds 131.46, 62.44, 217.53, 197.43, 183.72, 59.46 and 63.54 for 2019 to 2025; the figure above each bar is the whole number. 2018 (six months, 45.27) and 2026 (nine months, 47.04) are hatched.
2. The table **The last twelve months beside the long-run averages**: revenue 59.85, 102.24, 130.80; energy sold 2,580, 2,600, 2,422 MWh per MW; capture rate 72, 110, 98 percent.
3. Under **What it earned per MWh against the hub average**, the chart **Capture price against the hub average, by year, USD per MWh**. The percent above each pair: 177, 130, 55, 131, 146, 85, 76 for 2019 to 2025, 73 for 2026 (hatched), and 72 for **Last 12 months**. Say: the fleet was paid above the average until 2023 and below it since.
4. The table has 14 rows, **Hub average** in bold. Read two: **West hub** 18.47 against 30.63, 60 percent; **Houston hub** 27.26 against 32.88, 83 percent.

### Minute 2 to 3: another hub

1. Click **West hub** in the table. The address becomes `/cost-of-power/seller?iso=ercot&hub=HB_WEST#capture`.
2. The sentence now says "priced at the West hub (real-time prices)". Revenue reads 47.51 USD/kW and coverage 0.49 times (methods note 5.1). **Price received at the West hub** reads 18.47.
3. Say: same fleet, same hours, another price. This is hub to hub, not hub to node.
4. Click **Hub average** in the same table to go back. The address is now `/cost-of-power/seller?iso=ercot&hub=HB_HUBAVG#capture`, and every number is the default's again.

### Minute 3 to 4: is it worth building?

1. Scroll to **Is it worth building?**. **Scenario A** is in view; ten fields, each with its default and source in grey and a **Reset**.
2. Read the results table, headed **For 100 MW of solar**:
   - **The worst month**: USD 139,299, "February 2024, of 99 months; coverage that month 0.06 times".
   - **NPV at the hurdle rate**: USD -74.16 million, "USD -741.60 per kW at 12 percent".
   - **IRR**: none.
   - **Contract price at which coverage reaches 1.25 times**: USD 39.14, "on 2,580 MWh a year per MW".
   - **Breakeven PPA price**: USD 58.36, "on 100 percent of the energy for the debt's 35 years".
   - **Revenue with and without the battery beside it**: USD 11.64 million with, USD 6.33 million without.
3. Press **Make B a PPA**. **Scenario B** comes into view with **Contract share** 100 and **Contract price** 58.36. The address gains `bn=100&bp=58.36&v=b` (from a bare address it reads `?bn=100&bp=58.36&v=b`).
4. Column B's NPV is zero or just above (the check allows under USD 1 per kW). Column A has not moved, and the headline still reads A: 0.67 times.
5. Say the sentence beside the button: "A starting point to move to an offer in hand; no published price is held." Type an offer into **Contract price** to show it recompute. No expected number is held for a typed offer.

### Minute 4 to 5: what matters most

1. Press **Scenario A**, then scroll to **What matters most**: the chart **How far each assumption moves NPV, scenario A**, eight rows, longest first.
2. Read the top row and the bottom row (the screen drops a trailing zero):
   - **Capital cost** by USD 100 per kW: USD 8.21 million. Point at it: NPV is USD -65.95 million at 1,275 and USD -82.37 million at 1,475.
   - Then **Interest rate** 5.96, **Debt share** 4.10, **Fixed O&M** 4.09, **Degradation** 3.51, **Project life** 1.73, **Hurdle rate** 1.59, **Term of the debt** 1.16, all USD million.
3. Say: no one step of cost or financing brings USD -74.16 million to zero; the largest moves it by USD 8.21 million. A contract price of USD 58.36 does: that is the PPA row.
4. Close on the source line at the foot: "Checked against: 10 published figures (Lazard, the Annual Technology Baseline, EIA)." The two downloads, **Every month, CSV** and **The other tables, CSV**, hold the months, the stress days and every capture table.

**With a sixth minute.** `/cost-of-power/seller?asset=peaker`: **Margin over fuel, last twelve months** 48.15 USD/kW at the hub average and 59.58 at the West hub; the toll row reads USD 8.34 per kW-month. `/cost-of-power/seller?asset=battery`: 58.53 USD/kW, energy alone, with a link to What a battery earns.

**California, if asked.** `/cost-of-power/seller?iso=caiso` opens CAISO solar at SP15, held from September 2024. The methods note's section 12 holds what the page's files give for the last twelve months: revenue USD 28.45 per kW on 2,057 MWh per MW; price received 13.86 against a flat average of 28.53 (48.6 percent); coverage 0.23 times; breakeven PPA price USD 73.19 per MWh. Say: California's solar is paid under half the average price in the south (NP15: 73.0 percent), and one whole year is held, 2025. Read the screen for the figures themselves. California's stress days are not in this page's downloads: the model's snapshot holds them for ERCOT alone.

**If something goes wrong.** "In review" instead of the page: the internal view is not open in this browser. Open the unlock address again.

## Where the numbers in this document come from

"Methods note" is `docs/methods/generator_earns_algorithm.md`. Since `aa3addbc` the branch's files are on `main`, and "(branch)" below reads "on `main`"; session 260 checked that each file named exists there.

| Number | File | Section or line |
|---|---|---|
| 59.85; 102.24; 130.80; 23.27; 32.17; -8.90; -27.7 percent; 0.67; 8,736 hours; 80,832,584 MWh | Methods note | Opening "default case"; 4.2; 4.3 |
| USD 59,852.26 per MW; (5,985,226 - 1,250,000) / 7,078,769 | Methods note | 4.2; 4.3 |
| 82,500,000; 0.0858033; 7,078,769; the other assets' debt payments | Methods note; `site/scripts/test-seller-finance.mjs` | Section 2 "The debt default"; section 7; lines 50 to 53 |
| Revenue by year (45.27 to 47.04) | Methods note | 4.8 |
| The income table (2,580; 2,600; 2,422; 23.20; 72, 110, 98) | Methods note | 4.9 |
| Capture rate by year (177 to 73) and by hub (18.47, 30.63, 60; 27.26, 32.88, 83) | `docs/brand/review-235/numbers_before_after.txt` (branch) | Part 3 |
| NPV -74.16 million, -741.60 per kW; the eight bars; -65.95 and -82.37 million | `docs/brand/review-212/numbers_before_after.txt` (branch) | The `npv` cells and the bar lines `capex` to `term` |
| NPV -78.43 million at 9.6 (older, superseded) | Methods note; `SESSION_196_REPORT.md` | 11.4; the table of moved numbers |
| 39.14; 58.36; USD 550 of equity; 70.79; 2.580 | Methods note | 11.3 |
| Worst month 139,299, February 2024, 0.06 times; 11.64 and 6.33 million | Methods note; review-212 numbers | 11.4; the `month` and `battery` cells |
| `?bn=100&bp=58.36&v=b`; B's NPV under USD 1 per kW | `runs/session249/code_report_235.md`; `site/scripts/check-seller-scenarios.mjs` (branch) | "What to review", item 4; part 10b |
| Other hubs (47.51, 0.49; 72.48, 0.85); battery 58.53; peaker 48.15, 59.58 | Methods note; `SESSION_183_REPORT.md` | 5.1; "What to review" |
| Wind 56.85 on 3,028 MWh; peaker toll 8.34; battery toll 8.90 | Methods note; `SESSION_186_REPORT.md` | "Cross-checks"; lines 49 to 51 |
| Stress days (12,382,220; 18 days; 4,060,021) | Methods note | 4.16 |
| The ten published comparisons | Methods note | "Cross-checks" |
| 1,428 and 4,197 hours; 107.495 MW; 6,328,531; 364 days | Methods note | 3.2; 4.11 |
| Battery page: 81.40, 33 percent, 73.00, 148 and 55 | `docs/methods/battery_earns_algorithm.md` (branch) | "The default case"; "Cross-checks" |
| Reserve adders: 7.05, 0.07; hours of at least USD 100 | `docs/methods/ercot_rt_price_adders.md` (main) | "Hours a year with an adder above zero" |
| Every default, bound, step and label | `site/lib/seller/finance.ts`, `site/lib/merchant.ts`, `site/app/cost-of-power/seller/SellerForm.tsx`, `SellerScenarios.tsx`, `page.tsx`, `site/components/decisions/ScenarioBlock.tsx` (branch) | `SPECS`, `DEFAULTS`, `DEBT`, `HURDLE`, `TARGET` |
| Check counts (179, 106; 3,728; 4,249; 12 of 33) | `archive/sessions/SESSION_235_REPORT.md`; `archive/sessions/SESSION_241C_REPORT.md` | "Checks, with exit codes"; "The landing"; "Read these first" |
| California: 30.05, 6.95, 0.78; 41.47, 10.11, 3.52; 30.29, 35.53, 32.91, 32.97, 30.82, 2.15; 45.8, 71.7, 25.1; 72.58, 47.06; 79.50, 78.2; 26 months | Methods note | 12.1; 12.5 |
| California's default case: 28.45, 2,057, 13.86, 28.53, 48.6 and 73.0 percent, 0.23, 73.19; 2,477 and 3,125; 3,650 MW | Methods note; `docs/howitworks/computed/generator_caiso_check_2026-10-13.json` | 12.2; 12.3; 12.4 |
| The capture file's date and the default case recomputed from it (23.27, 32.17, 8,736, 80,832,584) | `site/data/seller/capture.json` | `built`; the twelve months of `grids.ercot.hubs`, `HB_HUBAVG`, `rt.solar` |
| Lazard's wind illustration; the hand check of 2025-07 | `docs/methods/cost_of_power.md` | "Debt service"; "Hand-computed checks" |
