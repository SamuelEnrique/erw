# Review pack: What a battery earns

- **Address:** `/cost-of-power/battery` (production `https://erw-flame.vercel.app/cost-of-power/battery`, opened after `https://erw-flame.vercel.app/internal/open`). Grids ERCOT and CAISO.
- **Status:** in review, like every page (`site/lib/release.ts`). A visitor sees the in-review page; the review needs the internal view.
- **Written from:** branch `wip/263-battery-pack`, base `afacb21e` (sessions 257, 258, 260 merged), with session 263's own commits. Date 2026-10-14.
- **Replaces** the how-it-works note of sessions 249 and 260 (the battery note of `docs/howitworks/`, removed in session 263). Every number of that note is here; its demo is the appendix.
- **Numbers:** read from the live table on 2026-10-14 (last twelve months October 2025 to September 2026). The figures the old note marked as computed for it alone are now in `docs/methods/battery_earns_algorithm.md`, section 11.2, and checked by `site/scripts/check-battery-figures.mjs` (32 of 32 on 2026-10-14). No figure here carries that mark.

## 1. What it is for, and for whom

- **The question:** what a grid battery of a given size and duration earned in ERCOT or CAISO from energy and ancillary services together, by year and by stream; did that cover its debt; is it worth building at stated costs; which assumption matters most.
- **For whom:** a developer or investor sizing a merchant battery; a lender who wants coverage and a bad month; an operator who wants a ceiling to set a real result against.
- **What it gives:** USD per kW of rated power, and US dollars for the reader's size.
- **Default case:** ERCOT, 4 hours, perfect foresight, 100 MW: USD 81.40 per kW over October 2025 to September 2026 (USD 8,140,219), 33 percent from ancillary services, a bad month of USD 475,477 (December 2024), debt covered 2.63 times on USD 2,261,119 a year, NPV USD -69.78 million at 12 percent, IRR -8.8 percent, breakeven toll USD 4.19 per kW-month.
- **What it is:** an upper bound on what the posted prices offered one small battery at the hub. The page says so under its chart.
- **What it is not:** a forecast, a valuation, what any real battery was paid, or advice. No sentence on the page says what to build.
- **Where it stops:** ERCOT from 2018-01-01, CAISO from 2024-09-01. NYISO and SPP are built and in review (internal view only). PJM, ISO-NE and MISO are words only: their prices are licensed.
- **Three questions on the page** (session 208): "What did it earn?", "Is it worth building?", "What matters most".

## 2. The model, step by step

1. **Prices come in.** ERCOT's hub energy prices at `HB_HUBAVG` (real time every 15 minutes, day-ahead hourly) and hourly day-ahead ancillary clearing prices (`warehouse/connectors/ercot_as_prices.py`); CAISO's SP15 hub and `warehouse/connectors/caiso_as_prices.py`. The model reads them in `energy_prices()` and `as_prices()` in `warehouse/derived/battery_stack.py`.
2. **A price becomes an hourly price** (`build_market()` in `warehouse/derived/battery_stack.py`): the mean of the hour's intervals, only when all are present (four of four for ERCOT real time). An hour with a missing interval has no price.
3. **A day is admitted or left out** (`build_market()`, `day_hours()`): a local day (23, 24 or 25 hours) is solved only when every hour has an energy price and a price for every product bought that day. Any other day is left out and counted. Nothing is filled or scaled.
4. **One linear program a day** (`solve_day()` in `warehouse/derived/battery_stack.py`, scipy's HiGHS): 1 MW split hour by hour between charging, discharging and an award of each ancillary product, each 0 to 1 MW.
5. **What it maximizes** (`structure()`): energy price times (discharge less charge), plus each product's capacity price times its award, summed over the day.
6. **Power limit** (`structure()`): discharge plus upward awards at most 1 MW; charge plus Regulation Down at most 1 MW. A megawatt is sold once.
7. **Energy limit** (`structure()`): every day starts empty; state of charge rises by 0.9274 of what is charged and falls by discharge over 0.9274 (the square root of 0.86), between 0 and the duration.
8. **Energy behind reserves** (`required_hours()`, `sides()`): each upward award must have stored energy for the product's required duration at the hour's start and end; Regulation Down needs room.
9. **One cycle** (`structure()`): energy taken out in a day at most one full charge.
10. **Reserves are not called:** an award is paid its price and moves no energy (`structure()`).
11. **Negative prices** (`solve_day(..., force_switch=True)`): a day that charges and discharges in the same negative-price hour is solved again with a charge-or-discharge switch. Needed once in 36 months exported: 2025-01-04.
12. **Every limit checked again** (`check_day()`): one violation stops the build.
13. **Days become months** (`monthly_rows()`): energy, each product and the total summed by local month into `battery_stack_monthly`, per MW, four decimals. A month with no solved day has no row, never a zero.
14. **The live set and the page's read** (`rowsOf()` in `site/app/cost-of-power/battery/read.ts`; a grid in review: `reviewRows()` from `site/data/battery_stack_review.json`): the rows of one hub, strategy and duration on each request.
15. **The address read** (`inputsOf()` in `site/lib/batterystack.ts`, `parseScenarios()` in `site/lib/battery/finance.ts`): every value defaulted and bounded. Since session 263 `typedNotes()` and `scenarioNotes()` say in one line what was not shown as asked.
16. **A month counts** (`monthsOf()` in `site/lib/batterystack.ts`): held when at least 90 percent of its days are solved (`NEAR`); whole when every day is in the table, solved or left out.
17. **The last twelve months** (`lastTwelve()`): the newest held and whole month and the eleven before it, all held. Headline: their total per MW over 1,000 (USD per kW), times the reader's MW (USD).
18. **A bad month** (`badMonth()`, `last36()`): the 10th percentile, nearest rank, of the held months among the 36 calendar months ending with the window's last month.
19. **Debt coverage** (`coverage()` in `site/lib/batterystack.ts`; with a contract `coverage()` in `site/lib/battery/finance.ts`): the twelve months' revenue for the size, less a year of fixed O&M, over a year of debt payments (`debtUsd()`). Default: `(8,140,219 - 2,200,000) / 2,261,119 = 2.63`.
20. **Is it worth building** (`resultOf()`, `flows()`, `npv()`, `irr()`, `breakevenToll()`, `merchantTail()` in `site/lib/battery/finance.ts`; drawn by `Scenarios` in `site/app/cost-of-power/battery/Scenarios.tsx`): the last twelve months repeated every year of the life, cut by degradation each year after the first; cash flow to equity, NPV at the hurdle rate, IRR by bisection, the breakeven toll, the merchant tail. In the browser; nothing is sent.
21. **What matters most** (`sensitivity()` in `site/lib/battery/finance.ts`, `BatterySensitivity` in `Scenarios.tsx`): each assumption moved down and up by its step, the others held, NPV recomputed, sorted by the larger move. Efficiency and cycles take only the model's own runs (`stepState()`, `cellTotals()`, `site/data/battery_scenario_steps.json`).
22. **The checks** (`site/scripts/check-values.mjs`, `site/scripts/check-battery-figures.mjs`): every keyed number on the page, and every figure of this pack, recomputed from the table by the page's own library.

## 3. Every assumption

"Fixed": the reader cannot change it. Labels in quotation marks are the page's.

| Assumption | Default | Source | Ruling of 12 October |
|---|---|---|---|
| Grid | ERCOT ("Grid") | ERW's choice of default | none |
| Where energy is priced | `HB_HUBAVG` (ERCOT); SP15, `TH_SP15_GEN-APND` (CAISO); fixed | ERW's assumption; a battery is paid its own node's price | none |
| History | ERCOT from 2018-01-01; CAISO from 2024-09-01; fixed | what the price tables hold | none |
| Duration | 4 hours ("Duration": 2, 4 or 8) | ERW's choice; the ERCOT fleet's mean was 1.50 hours in 2025 (`docs/methods/battery_early_years.md`) | none |
| Size | 100 MW ("Size, MW", 1 to 5,000) | ERW's choice; every result is linear in MW, itself an assumption | none |
| Strategy | perfect foresight: energy at the hourly real-time price, ancillary at day-ahead prices, all known in advance | ERW's definition of an upper bound | none |
| Day-ahead schedule | day-ahead energy and ancillary prices; every offer clears; no real-time trading | ERW's definition | none |
| Price taker | awards 0 to 1 MW per MW at the posted price, whatever the market's size; fixed | ERW's assumption; tested in session 74 | none |
| Reserves called | never; fixed | ERW's assumption; tested in session 79 | none |
| Round-trip efficiency | 86 percent, split evenly ("Round-trip efficiency": 86, 89, 92) | Lazard LCOS v10.0: 86 to 92 percent; the model runs at the low end | none |
| Cycles | at most one a day ("Cycles a day, at most": 0.5, 1, 1.5, 2) | ERW's choice (the seller tab's rule); the other steps are the reader's | none |
| Start of day | empty; nothing carried over midnight; fixed | ERW's choice (the seller tab's rule) | none |
| Resolution | hourly; fixed | ancillary prices are hourly | none |
| ERCOT products | Regulation Up and Down, Responsive Reserve, Non-Spin, ECRS from 2023-06-10 | `ercot_as_prices`, day-ahead clearing prices | none |
| CAISO products | Regulation Up and Down, Spinning and Non-Spinning Reserve, region `AS_CAISO_EXP` | `caiso_as_prices` | none |
| Energy behind ERCOT Regulation and Responsive Reserve | 1 hour to 2025-12-04; 30 minutes from 2025-12-05 | before: assumed, not verified; from: ERCOT NPRR 1282 | none |
| Energy behind ECRS | 2 hours from 2023-06-10; 1 hour from 2025-12-05 | ERCOT NPRR 1096; NPRR 1282 | none |
| Energy behind Non-Spin | 1 hour to 2022-12-08; 4 hours from 2022-12-09 | before: assumed; from: NPRR 1096 | none |
| Energy behind CAISO regulation; reserves | 1 hour (day-ahead awards); 30 minutes | CAISO tariff, sections 8.4.1.1(g) and 8.4.3 | none |
| A day with a missing hour | left out whole, counted | ERW's rule: never filled | none |
| A month counts | 90 percent of its days solved | the seller tab's rule | none |
| The last twelve months end | with the last complete month | the owner's ruling of 2026-10-11 (session 195) | none |
| A bad month | 10th percentile, nearest rank, of 36 calendar months | ERW's choice (session 71) | none |
| The one month set aside | above 25 percent of everything held: its share is said under the table, and the reader can leave its event out of the window (session 296: the column without it is gone, no window being the ERW's) | ERW's choice (session 71); the ruling of 15 October, item 6 | none |
| Chart scale | "adjusted" by default: broken when the tallest year is above 2.5 times the second; the reader can choose linear or log (session 296) | ERW's choice; the ruling of 15 October, item 5 | none |
| The income table's columns | the last twelve months, each calendar year held, and one window the reader sets (its first and last year; the grid's stress events left out by a checkbox each), which opens on every year held with nothing left out, the old average (session 296) | the ruling of 15 October, item 6: no window is the ERW's | none |
| Capital cost | 610, 1,110, 2,300 USD per kW (2, 4, 8 hours) | Lazard LCOE+ June 2025, LCOS v10.0, midpoints of 340 to 880 and 620 to 1,600; 8 hours NREL's Annual Technology Baseline 2025 (Cole, Karmakar and Mann, NREL/TP-6A40-93281, June 2025, section 2.2: USD 241 per kWh times 8 hours plus USD 372 per kW, 2024 dollars), 2,110 by a straight line through Lazard's two until session 296 | the ruling of 15 October, item 8 |
| Fixed O&M | 11.2, 22, 92 USD per kW a year | the same Lazard cases; 8 hours the ATB's 4 percent of its capital cost a year, which pays for augmentation (43.6 by the straight line until session 296) | the same |
| Sensitivity mode | the sourced range by default: each assumption between its published low and high case (Lazard's two cases, and the ATB's figures where it states one), in NPV; or a percent step the reader sets (10 by default, 1 to 100), in NPV or IRR, efficiency and cycles snapping to the steps the model was run at (session 296) | the ruling of 15 October, item 7; `rangesOf` in `site/lib/battery/finance.ts`, the shape `site/data/sourced_ranges.json` will take | none |
| Debt share | 20 percent of capital cost | Lazard's storage cases: "20% debt at an 8% interest rate and 80% equity at a 12% cost" | "the debt share's default is Lazard's storage capital structure, 20 percent" (60 until session 208) |
| Interest rate | 8 percent a year | the same | the same ruling |
| Term of the debt | 20 years, level payments, cut to the life if longer | Lazard: 20 years for storage | none |
| Degradation | 2.6 percent a year, as a cut to revenue | Lazard LCOS v10.0, 2 and 4 hours; 8 hours takes the same | the ruling of 11 October (session 196): a cited default |
| Project life | 20 years | Lazard | none |
| Hurdle rate | 12 percent a year | Lazard's cost of equity | "the hurdle rate's default is Lazard's cost of equity, 12 percent": the NPV is to equity |
| Contract | share 0, price 0: fully merchant | none: the reader's own term; no published price held | the contract is two scenario assumptions (session 208) |
| How a contract runs | for the debt's years, flat price; the contracted share earns nothing from the market | ERW's choice (session 208) | the same ruling |
| Future revenue | the last twelve months, every year of the life | ERW's assumption, not a forecast | none |
| Tax, tax credit, augmentation, residual value, inflation | none modeled | ERW's choice | none |
| Breakeven toll | the price at which coverage is 1.25 | ERW's choice; the code cites no source for 1.25 | none |
| IRR search | -99 to 1,000 percent a year; outside it "none" | ERW's choice | none |
| Steps of efficiency and cycles | the model's own runs, nothing interpolated; withdrawn when a month of the table differs by more than half a cent per MW | `site/data/battery_scenario_steps.json` | none |
| Sensitivity rows | ten at the defaults; the contract's two only when scenario A holds a contract | `sensitivity()`, session 211 | the ruling of 12 October (session 211) |
| The sourced range at 8 hours, and the contract | 8 hours takes the ATB's figure alone, no range for its capital cost and fixed O&M (four rows where 2 and 4 hours draw six); the contract's share and price take no sourced range, the percent step moves them; the year chart alone is the default chart | `rangesOf`, `noRangeOf` in `site/lib/battery/finance.ts`, session 314 | the ruling of 19 October 2026 (session 296's three open items) |
| The awards line (ERCOT) | January to July 2026, the months both tables hold whole | `site/data/battery_awards_beside.json` | none |
| California's line beside its market monitor | 2025, 4 hours, day-ahead: the model's energy and regulation from the table; the real fleet's 35 and 9 typed from the report | `FLEET_BESIDE` in `site/lib/batterystack.ts`; CAISO DMM, 2025 Annual Report, section 1.3.3, Tables 1.7 and 1.8 | none |
| Rounding | table four decimals; USD a whole dollar; USD per kW two decimals | the code | none |
| Sensitivity steps | capital USD 100 per kW; debt share 10 points; interest 1 point; term 5 years; fixed O&M USD 5; efficiency 3 points; cycles 0.5; degradation 1 point; life 5 years; hurdle 1 point; contract share 10 points; contract price USD 1 | ERW's choice | none |
| Bounds of the typed fields | size 1 to 5,000 MW; capital 0 to 10,000; debt share 0 to 100; interest 0 to 30; term and life 1 to 40 whole years; fixed O&M 0 to 500; degradation 0 to 20; hurdle 0 to 40; contract share 0 to 100; price 0 to 100 | `SPECS` in `site/lib/battery/finance.ts`, `inputsOf()` | none |

## 4. The cross-checks

"Gap" is ours less theirs, USD per kW unless said. Most rows set one modeled battery beside a fleet: a gap is not an error to be closed.

| What is compared | Ours | Theirs | Gap | Reason |
|---|---|---|---|---|
| ERCOT, day-ahead ancillary income, January to July 2026, a month (ERCOT's own awards to storage) | 2.25 | 0.40 | +1.85; 5.66 times | the model holds 142 percent of its power in awards in the mean hour, the fleet 21.6; regulation alone 122 against 4.4 |
| ERCOT, 4 hours, 2024 (Modo Energy, fleet average) | 148 foresight; 127 day-ahead | 55 | +93; +72 | one price-taking battery at the hub against a fleet at its nodes, mostly 1 and 2 hours |
| ERCOT, 4 hours, 2025 (Modo, through November; nowcast for the year) | 87; 78 | 26.0; 29.4 | +58; +49 | the same; ours over theirs 2.7 and 3.0 in the two years |
| ERCOT 2024 and 2023 (E3, a modeled 2-hour battery at ERCOT North) | 148 and 530 foresight; 127 and 459 day-ahead | about 127; up to about 475 | 2024 +21, 0; 2023 +55, -16 | the closest method to ours; 2 hours at North against 4 at the hub average |
| ERCOT, first half of 2025, a month (Tyba) | 7.3 | 2.13 median asset; 6.19 the best | +5.2; +1.1 | ours above the best asset, as an upper bound should be |
| ERCOT market revenue, February to July 2026 (the fleet's awards plus real-time deviations) | 18.81 (2-hour day-ahead schedule) | 7.17 (4.17 + 3.00) | +11.64 | the fleet figure leaves out contracts, node prices and real-time ancillary money |
| ERCOT day-ahead only, January to July 2026 | 30.14 (2-hour day-ahead) | 6.53 (the fleet's awards) | +23.61 | never offered 9.70 (an allocation); price -0.62; offered and not awarded 14.53 |
| ERCOT's market monitor, 2024 report (Potomac Economics) | none | no storage net revenue published | none to compute | its net revenue analysis covers gas, wind and solar |
| CAISO 2025, 4 hours, day-ahead, run the market monitor's way | 84.72 | 77.3 ("CAISO System", Table 1.8) | +7.4 (10 percent) | one hub against more than 280 nodes; their regulation moves energy; their month-long horizon has no cycle limit; not separated |
| The same by quarter | 29.23; 24.30; 17.45; 13.75 | 28.8; 22.8; 14.2; 11.5 | +0.4; +1.5; +3.3; +2.3 | same shape; the third quarter's gap not explained |
| CAISO 2025, the split, their way: energy; regulation | 41.89; 42.83 | 39; 39 | +2.9; +3.8 | both models earn about half from each |
| CAISO 2025, the page's model, day-ahead | 85.34 | 77.3 | +8.0 | the two reserves add 0.77; round trip 0.86 against 0.85 |
| CAISO 2025, the page's model, perfect foresight | 91.74 | 77.3 | +14.4 | an upper bound against a day-ahead schedule |
| CAISO 2025, the real fleet: energy; regulation (the page's line) | 42.31; 42.25 | nearly 35; 9 | +7.3; +33.3 | the whole gap is regulation: the model sells as if the market had no size; the monitor: "a large amount of battery capacity competing to provide a relatively low amount of required regulation" |
| CAISO 2025, the southern areas: LA Basin; Big Creek/Ventura; San Diego/Imperial | 84.72 | 62.6; 64.2; 66.3 | +22.1; +20.5; +18.4 | not explained: how their nodes map to SP15 was not checked; Greater Fresno is 111.7 |
| CAISO 2022 to 2024, the fleet (DMM special report, May 2025) | no whole year held | 103; 78; 53 | none to compute | CAISO prices held from 2024-09-01 |
| Revenue against Lazard's levelized cost of a 4-hour battery | 81.40 (last twelve months) | 144.90 to 320.04 per kW-year | -63.50 to -238.64 | Lazard's cost also pays charging energy, augmentation, taxes and a 12 percent return on equity |
| Round-trip efficiency | 86 percent | 92 to 86 (Lazard); 85 (ATB) | 0 to -6; +1 | the low end of Lazard's range |
| Fixed O&M, 4 hours | 22 | 44.40, the ATB's 4 percent of capital cost | -22.40 | the ATB pays augmentation inside fixed O&M; Lazard does not |
| Project life | 20 years | 15 years (ATB) | +5 | Lazard's storage cases run 20 |
| Debt share | 20 percent | 20 percent (Lazard's storage cases) | 0 | ruled 12 October; 60 until session 208 |
| SP15 day-ahead peak block, January to September 2026, USD per MWh | 24.04 | 23.97 (ICE's index in EIA's file) | +0.07 | a traded expectation against the cleared price |
| The optimizer, all 1,096 exported days | the model's day | an independent solve and a ceiling needing no solver | largest relative gap 3.2e-10; ceiling reached on 1,095 days | the one other day is the switch day, 2025-01-04, USD 0.038 below the linear ceiling |
| Reserves called, ERCOT, 2018-01-01 to 2024-07-31 | 393.1 and 530.1 (2022, 2023) | 401.8 and 562.3, called on ERCOT's own event lists | within 0.1 percent 2018 to 2020; 0.9 below in 2021; above from 2022 | energy delivered on call is paid a scarcity price |
| A cap by the market's size, ERCOT, 2026-09-03 to 2026-10-02 | 5.92 (price taker) | 4.52 (fleet-limited) | the capped battery earns 69 to 82 percent | caps average 2.6 percent of power for regulation, 9 for ECRS, 13 for Responsive Reserve and Non-Spin |

- The page's source line says "Checked against: 15 published figures" (14 until session 297, which set the fade method beside the ATB's convention); the rows above are those and the model checks beside them.
- Not held: no published 2025 ERCOT figure from ERCOT's market monitor (its report has none); no Berkeley Lab figure for storage revenue is quoted on this page.

## 5. The edge cases tested

Tested on 2026-10-14 on a local production build of this branch (port 3263, internal view, 32 addresses and four typed values) by `runs/session263/edges.mjs` on the old laptop (not in git; its output `runs/session263/edges.txt`); the library cases are held by `tests/test_session263.py`. Two wrong behaviours were fixed at their cause (no debt; a term above the life); no fix changed the layout. Addresses are relative to `/cost-of-power/battery`.

| Case | What was typed (the address) | What the page does |
|---|---|---|
| A grid the tool does not hold | `/cost-of-power/battery?grid=xyz` | ERCOT's page, with one status line (new, session 263): "The grid asked for is not a grid this tool holds: ERCOT is shown." Until session 263 ERCOT was shown with no word |
| A grid named but not built (licensed) | `?grid=pjm`; `?grid=miso` | ERCOT's page and "PJM is not built for this tool (license needed): ERCOT is shown."; "MISO is not built for this tool (held, not shown: license needed): ERCOT is shown." |
| A grid in review, outside the internal view | `?grid=nyiso` (library: `typedNotes()` with `internal` false) | ERCOT's page and "NYISO is in review and opens in the internal view only: ERCOT is shown." In the internal view NYISO opens with no such line |
| A held grid, an 8-hour case in review | `?grid=nyiso&dur=8&strat=foresight`; `?grid=spp&dur=8&strat=dayahead` | Both open with their in-review line: NYISO USD 222.11 per kW, 71 percent ancillary, 4.15 times, a bad month of 23 months; SPP 178.50, 65 percent, 3.14 times, 25 months. No held grid lacked rows for any of its six cases tonight, so the empty-case line ("No month is held for this battery in ...") was not reached by an address; it stands in `page.tsx` |
| 1 MW | `?mw=1` | USD 81.40 per kW (per kW figures do not move); bad month USD 4,755; debt USD 22,611 a year; NPV USD -697,799; no line |
| 1,000 MW | `?mw=1000` | USD 81.40 per kW; bad month USD 4.75 million; debt USD 22.61 million; NPV USD -697.8 million; no line |
| A size outside 1 to 5,000 | `?mw=0`; `?mw=99999`; `?mw=abc` | Brought to 1 MW, to 5,000 MW, or the default 100, each with a line: "0 MW is outside the size field's bounds, 1 to 5,000 MW: 1 MW is shown."; "99,999 MW ...: 5,000 MW is shown."; "The size asked for is not a number: 100 MW is shown." (new, session 263) |
| 8-hour duration | `?dur=8`; `?grid=caiso&dur=8&strat=dayahead&mw=1000` | ERCOT: USD 98.94 per kW, 25 percent ancillary, 1.29 times, NPV USD -169.85 million, IRR "none" (no rate from -99 to 1,000 percent sets NPV to zero). CAISO 1,000 MW: 86.03, 33 percent, 0.99 times, NPV USD -1.78 billion, IRR none, 25 months |
| A duration or strategy not run | `?dur=3`; `?strat=other` | 4 hours or perfect foresight, with "The model is run at 2, 4 and 8 hours: 4 hours is shown." or "The strategy asked for is not one of the two: perfect foresight is shown." |
| A debt term longer than the project | `?at=30` | The debt is repaid over the life (`debtYears()`: 20 years); headline unchanged (2.63 times, USD 2.26 million a year). Fixed tonight: the tail's note read "the term and the life are both 20 years" with a term of 30; it now reads "0 years: the term of 30 years is cut to the life, 20 years" |
| A life longer than the term | `?al=30` | Tail USD 1.28 million, years 21 to 30; NPV USD -68.5 million; IRR -2.6 percent |
| A term above a shorter life | `?at=25&al=15` | Debt over 15 years: USD 2.59 million a year, coverage 2.29 times, NPV USD -72.55 million, IRR -13.2 percent, tail "the term of 25 years is cut to the life, 15 years" |
| A contract longer than the project | `?an=50&ap=10&at=30` | The contract runs the debt's years, cut to the life (20): coverage 3.48 times, NPV USD -51.13 million, IRR 0.7 percent; the headline sentence names the contract |
| No debt at all | `?ac=0`; `?as=0`; `?ac=-5` | Fixed tonight: the sentence read "covered its debt not held times". It now reads "... and has no debt to cover."; the headline number reads "No debt"; scenario A's coverage and toll read "no debt"; NPV USD 35.91 million at a capital cost of 0 |
| A leap year | the table's February 2024 (and 2020) | 29 of 29 days held, counted. The 90 percent rule on 29 days needs 27 (26 of 29 is 89.7 percent, not counted; 27 is 93.1): `monthsOf()` reads the month's own `days_in_month`, tested in `tests/test_session263.py`. The finance has no day count: a year is twelve monthly sums, NPV and IRR are yearly |
| A month with one day held | the newest partial month, October 2026 (12 of 31 days on 2026-10-14; one day on the 2nd of any month) | Not counted: not in the last twelve months, not in the bad month's 36, grey in the CSV of every month. A month of 1 day of 31 is tested in `tests/test_session263.py`: not held, not whole, not in the window |
| A month at the 90 percent line | CAISO April 2025: 27 of 30 days (three left out, no reserve prices) | Counted (exactly 90 percent), with its solved days' revenue only, not scaled |
| A typed value outside a field's bounds, in the address | `?ac=99999`; `?bh=50`; `?at=20.5`; `?ae=90`; `?ay=3`; `?ac=abc` | Brought inside, with one status line each (new, session 263): "Capital cost, scenario A: 99,999 is outside the field's bounds, 0 to 10,000 USD per kW, so 10,000 is used."; "Hurdle rate, scenario B: 50 ... so 40 is used."; "Term of the debt, scenario A: 20.5 is not a whole number of years, so 21 is used."; "Round-trip efficiency, scenario A: 90 is not a step the model was run at, so 86 is used."; cycles 3: 1 is used; "abc": the default 1,110 |
| A typed value outside a field's bounds, typed in the field | capital cost 99999; term 20.5; fixed O&M -3 (typed in the browser) | Brought inside by `bound()` and, new tonight, said under the field while the value is in force: "99,999 was typed: the field runs from 0 to 10,000, so 10,000 is used."; "20.5 was typed: the field takes whole years, so 21 is used."; "-3 was typed: the field runs from 0 to 500, so 0 is used." The box keeps showing what was typed until it loses focus (the shared block's rule); typing 1200 removes the capital cost's line |
| The size field typed above 5,000 | the panel's "Size, MW" then "Show" | The field holds `min=1 max=5000`; a value past it goes to the address and is brought to 5,000 with the status line above |

## 6. What the model cannot see, ranked

Ranked by the number held, as far as numbers in different units can be set side by side; the last group holds no number.

1. **The years ahead.** The NPV repeats one window of price years for 20 years. Since session 352 (20 October 2026) the reader chooses it in the box ("Price years", read from `price_years_by_window`): the last twelve months (the default, USD 81.40 per kW at ERCOT, 4 hours, perfect foresight), any calendar year held (243.69 in 2018 to 3,430.56 in 2021, 87.44 in 2025), the last three full years averaged (255.08), the last seven (739.80), every month held (614.58), or every month held with a stress event taken out (269.52 without Uri's days). Scenario A and B, the results, the sensitivity and the headline follow the window, at the model's own efficiency and cycles; a line under the results gives the same project's highest and lowest whole year with scenario A's NPV in each. NPV reaches zero at the defaults at about USD 190 per kW a year. No forecast is held: the page shows the range of the years held, not the years ahead.
2. **The size of the ancillary markets.** ERCOT: USD 2.25 per kW a month against the fleet's 0.40 (January to July 2026); capped by the market's size the battery earns 69 to 82 percent of the price taker's figure (30 days of 2026). CAISO: regulation USD 42.25 per kW in 2025 against the real fleet's 9. Direction: the page is too high.
3. **Operation.** Perfect foresight against the day-ahead schedule: USD 81.40 against 73.00 over the last twelve months; 10.0 percent of the page's figure in 2025. Real assets: a median USD 2.13 per kW a month and a best of 6.19 in the first half of 2025 (Tyba). One real operator: no number held.
4. **The node.** Session 358 (`node_basis_daily`, `node_basis_summary`, `docs/methods/node_basis.md`): the twelve months of ERCOT's day-ahead prices at every storage settlement point, 1 October 2025 to 30 September 2026 (335 days; 21 August to 19 September 2026 not yet held), against `HB_HUBAVG`. Of the 195 storage points held 90 percent of the days, the median point's mean basis was USD 1.31 per MWh (10th percentile -4.07, 90th 5.78), its daily four-hour spread 49.31 against the hub's 47.26, and 57.4 percent of the points had a wider spread than the hub. Real time is held for 20 days only (28 September to 18 October 2026; ERCOT's list keeps seven days): the median storage point's spread 62.08 against the hub's 50.75, 76.3 percent wider, median basis 3.14. (The week of 28 September to 4 October, by four hours of hourly means: 44.11 at the median point against the pack's earlier 44.29 by 16 intervals.) CAISO: the monitor's model runs from 62.6 (LA Basin) to 111.7 (Greater Fresno) around 77.3. Direction: either, and in ERCOT's year the median storage point earned a little more spread than the hub. Applied to no figure of the page.
5. **Degradation.** No capacity fade in the model; the scenario cuts revenue 2.6 percent a year. One point either way moves the default NPV by USD 3.02 million. Augmentation: none modeled; the ATB's convention would about double fixed O&M (44.40 against 22).
6. **Reserves that are called.** Within 0.1 percent of the page 2018 to 2020, 0.9 percent below in 2021, above in 2022 and 2023 (401.8 against 393.1; 562.3 against 530.1). Regulation's energy is not in that test.
7. **Each day from empty.** The first hour of each day holds no upward reserve: at most USD 1.29 per kW over the last twelve months, 1.6 percent of 81.40 (page slightly low). Energy left at midnight averages 0.023 MWh per MW.

No number held:

- California's resource adequacy contract (not in the warehouse): revenue the page does not show for a California battery.
- Taxes and tax credits: none in the NPV.
- ERCOT real-time ancillary prices since 2025-12-05: not held, so ancillary income is day-ahead under both strategies.
- Trading inside the hour: the model is hourly.
- Outages and station power.
- Scarcity adders: `ercot_rtm_price_adders` (session 244) is read by neither the model nor the page.

## 7. The ten hardest questions

### 1. Your battery knows tomorrow's real-time prices. What does it earn without that?

- Day-ahead schedule: USD 73.00 per kW over the last twelve months against 81.40 with foresight.
- That schedule is still perfect against day-ahead prices and assumes every offer clears.
- What a real operator captures is not held; the only measure is the fleet's spread: median USD 2.13 per kW a month, best 6.19, the model 7.3 (first half of 2025).

### 2. Ancillary markets are small. What is left when 20,000 MW chase them?

- Less than the page shows; the page says so under the income table.
- January to July 2026: the model USD 2.25 per kW a month of day-ahead ancillary income; ERCOT's storage resources (17,180 to 21,365 MW) were awarded 0.40.
- Capped by ERCOT's own quantities over the fleet: USD 4.52 against 5.92 over 30 days of 2026, the ancillary stream falling about four fifths. That estimate is for review and not on the page.

### 3. How far is the model from what real batteries were paid?

- ERCOT, about three times with foresight: USD 148 against the fleet's 55 in 2024; 87 against about 29 in 2025 (Modo Energy).
- Down the ladder of `docs/methods/battery_early_years.md`, 2025: 87.4 (the page), 78.7 (day-ahead), 46.2 (the fleet's duration), 36.7 (no regulation), 28.5 (energy only).
- February to July 2026 in the warehouse's own data: the fleet's awards plus real-time deviations USD 7.17 per kW; the 2-hour day-ahead model 18.81.

### 4. Where is degradation?

- Not in the model: the battery holds its rated duration every day of every year.
- The finance block cuts revenue 2.6 percent a year (Lazard): a haircut, not fade (fade shortens duration and revenue is not proportional to duration).
- One point either way moves the default NPV by USD 3.02 million. Augmentation, outages, station power: no number held.

### 5. Does the battery have the energy behind the reserves it sells, and what if it is called?

- It has the energy: each upward award is backed for its required duration at the hour's start and end; the build stops if not. Non-Spin needs 4 hours, so a 2-hour battery holds at most 0.464 MW of it per MW.
- It is never called. On ERCOT's own event lists (2018-01-01 to 2024-07-31) being called changed the year by under 1 percent before 2022 and raised it after.
- It ran 0.983 cycles a day over the last twelve months; 1.5 cycles would lift the twelve months from 81.40 to 83.57.

### 6. ERCOT changed its market on 2025-12-05 (RTC+B). Is the model still right?

- Partly. It applies the new required durations from that day (30 minutes for regulation and Responsive Reserve, 1 hour for ECRS; NPRR 1282).
- It still pays ancillary services at day-ahead prices under both strategies: real-time ancillary prices are not held.
- The last twelve months (October 2025 to September 2026) fall after the change except two months and four days: the headline is mostly the new design's.

### 7. Can the CAISO result be trusted?

- For energy, within about a fifth; for regulation, no.
- Run the monitor's way: USD 84.72 per kW for 2025 against its 77.3, tracking it by quarter.
- Real batteries were paid about 35 for energy and 9 for regulation; the model takes 42.31 and 42.25. The page's line now says why (session 263): the model sells regulation as if the market had no size; the monitor writes that "a large amount of battery capacity" competes "to provide a relatively low amount of required regulation".
- 25 months held, one full year; no resource adequacy payment in the figure.

### 8. The chart shows USD 3,431 per kW in 2021. Did anyone earn that?

- Not held. It is what the posted prices offered: USD 2,841.6 of the year's 3,430.6 is seven days, 13 to 19 February (Winter Storm Uri).
- February 2021 alone is 57 percent of everything the default battery earned in every month held; the table gives the every-year average with it (614.58) and without it (269.68).
- The fleet was 821 MW at the end of 2021, mean duration 1.23 hours; the page's shortest battery holds 2.

### 9. The NPV is USD -69.78 million. Is the tool saying do not build?

- It says a number. USD 81.40 per kW less fixed O&M of 22 is 59.40 a year, worth USD 444 per kW over 20 years at 12 percent, against 888 of equity.
- Revenue would need to be about USD 190 per kW a year; ERCOT paid that to this battery only in 2021, 2022 and 2023.
- Capital cost USD 620 per kW: USD -23.12 million, IRR 2.1 percent. Half the battery contracted at USD 10 per kW-month: USD -51.13 million, coverage 3.48.
- Coverage of 2.63 is not in tension: the year's revenue pays the year's debt at 20 percent debt; it does not pay equity 12 percent.

### 10. My battery is at a node and has a toll. Does the tool see either?

- The node, no: energy is priced at the hub; the one week of node prices held is applied to nothing.
- The toll, as two numbers the reader types: "Contract share" and "Contract price". No published contract price is held; the default is fully merchant.
- The breakeven toll at the defaults is USD 4.19 per kW-month: the price on the whole battery at which coverage is 1.25.

## 8. What Samuel's Stata run must reproduce

The default case (ERCOT, 4 hours, perfect foresight, 100 MW, the page's defaults). The CSV's months are 2023-10 to 2026-09 and its `in_last_twelve` marks 2025-10 to 2026-09: the page's current twelve on 2026-10-14 (October 2026 is not complete). The Python mirror was run on the CSV; the page's library was run on the same months (each month the sum of its hours); the two agree on every value below. Stata is not on the machine that wrote the do-file: **the do-file was not run.**

| Name | The page shows | Python mirror | Library on the CSV's months | The do-file's display line |
|---|---|---|---|---|
| Last twelve months, all streams, USD per kW | 81.40 | 81.40 | 81.40 | `last twelve months, all streams, USD per kW:` |
| Last twelve months, total, USD for 100 MW | 8,140,219 | 8,140,219 | 8,140,219 | `last twelve months, total, USD for 100 MW:` |
| Energy; ancillary, USD for 100 MW | 5,459,858; 2,680,361 | the same | the same | `last twelve months, energy, ...`; `..., ancillary, ...` |
| Regulation Up; Down; Responsive Reserve; ECRS; Non-Spin | 664,224; 998,971; 402,471; 194,068; 420,627 | the same | the same | `last twelve months, regup, ...` and the four others |
| Share from ancillary services, percent | 33 | 33 | 33 | `share from ancillary services, percent:` |
| Annual debt payments, USD | 2,261,119 | 2,261,119 | 2,261,119 | `annual debt payments, USD:` |
| Debt coverage, times | 2.63 | 2.63 | 2.63 | `debt coverage, last twelve months, times:` and `scenario A, debt coverage, times:` |
| NPV at the hurdle rate, USD per kW | -697.80 | -697.80 (-697.7988270084118) | -697.80 (-697.7988270084116) | `scenario A, NPV at the hurdle rate, USD per kW:` |
| NPV, USD for 100 MW | -69.78 million | -69,779,883 | -69,779,883 | `scenario A, NPV at the hurdle rate, USD for 100 MW:` |
| IRR, percent a year | -8.8 | -8.8 (-8.80908509567243) | -8.8 (-8.80908509567243) | `scenario A, IRR, percent a year:` |
| Breakeven toll, USD per kW-month | 4.19 | 4.19 | 4.19 | `scenario A, breakeven toll, USD per kW-month:` |
| Merchant tail | USD 0 (0 years) | 0 years, 0 | 0 years, 0 | `scenario A, merchant tail, years:` |
| A bad month, USD for 100 MW | 475,477 (December 2024) | 2024-12, 475,477 | 2024-12, 475,477 | `a bad month:` |
| Months held of the 36 | 36 | 36 | 36 | `months held of the 36:` |
| 2024: energy; ancillary, USD per kW | chart 148 (62.70 + 84.98) | 62.70; 84.98 | 62.70; 84.98 | `calendar year 2024, months held:` |
| 2025: energy; ancillary, USD per kW | chart 87 (57.39 + 30.05) | 57.39; 30.05 | 57.39; 30.05 | `calendar year 2025, months held:` |

- Not in the CSV (they need years before October 2023): 255.08, 614.58, 269.68, 57 percent, the stress days, the sensitivity chart. `site/scripts/check-battery-figures.mjs` and `check-values.mjs` recompute them from the table.
- The do-file mirrors `site/lib/battery/finance.ts` line for line: `debtYears()` as `s_debt_years_used`, `crf()` as `s_crf`, `flows()` and `npv()` as the program `erw_npv`, `irr()` as the bisection loop, `breakevenToll()` and `merchantTail()`.
- The comparison, value by value, is in `runs/session263/replication_py.txt` and `runs/session263/compare_lib.txt` on the old laptop.

```
cd site/public/battery
do erw_2026_battery_replication.do
```

The Python mirror, for a reader without Stata: `python erw_2026_battery_replication.py` in the same folder.

## 9. Questions only Samuel can answer

1. **Should CAISO's line beside the market monitor follow the reader's battery?** (sessions 257, 253) Today it is always the 4-hour battery on the day-ahead schedule, whatever the panel holds, and says so. (a) keep it fixed: the monitor's case is that battery; (b) follow the reader's duration and strategy: the model's two figures move, the monitor's do not, so the comparison loses its like-for-like; (c) show both. One line of `page.tsx` either way.
2. **Berkeley Lab's terms page** (sessions 253, 257): it was not read; its figures are counted on the generator page, none on this one. (a) quoting with the source is enough; (b) read and record its terms in `docs/licenses.md` before 21 October; (c) drop its figures.
3. **Pull CAISO's price history before September 2024?** (session 246) About 39 months are served. (a) yes: California from mid 2023, the 2023 and 2024 summers in the stress table, a bad month on 36 months; (b) no: the page keeps saying "held from September 2024".
4. **Read CAISO's notices on a schedule?** (session 246) Held to 30 April 2025 on the data machine's last pull, so later stress events depend on a manual read. (a) one scheduled request for one PDF; (b) leave it manual.
5. **The January 2025 CAISO event** (session 246) is in the stress table by the rule. (a) keep it; (b) a floor (for example a day-ahead hour above USD 200) that would drop it, a judgment the rule now avoids.
6. **The southern areas' gap** (session 246): our SP15 at 84.72 against LA Basin at 62.6. (a) a session with CAISO's node list; (b) leave it written as not explained.
7. **Modo Energy's two rows** (session 208): its terms forbid redistributing its analysis; one figure each is quoted with the source. (a) keep as citations; (b) drop them and say "14" becomes "12".
8. **The breakeven toll's 1.25** has no source in the code (session 249). (a) cite a lender's convention; (b) write "ERW's choice" beside it on the page; (c) leave as is.
9. **A cap by the market's size on the page?** The fleet-limited estimate (69 to 82 percent of the price taker's figure) rests on 30 days of ERCOT quantities. (a) a line under the income table now; (b) wait for a year of quantities; (c) never: the page is an upper bound by definition.
10. **Degradation's source** (session 196): Lazard's 2.6 percent goes with Lazard's costs; the ATB holds none (augmentation inside fixed O&M). (a) keep Lazard's; (b) the ATB's convention: 0 percent and fixed O&M of 44.40.
11. **Stata: who runs the do-file once?** (session 249) (a) Samuel on his machine with the command of part 8; (b) leave it to the Python mirror.
12. **The clamp lines of session 263** (part 5): a value typed outside a field's bounds is brought inside them and a line says so. (a) keep the words; (b) refuse the value instead (the field keeps the old value): a behaviour change on the three decision pages, not made here.

## Appendix: the five-minute demo

Written from the page's code and its check scripts on 2026-10-13 (session 249), checked against the local build of 2026-10-14. Open the internal view first: `https://erw-flame.vercel.app/internal/unlock?token=<your internal token>` (or the form at `/internal/open`), then `https://erw-flame.vercel.app/cost-of-power/battery`.

**Say this first:** this is what the posted prices offered one small battery at the hub, split hour by hour so nothing is counted twice. It is a ceiling, and the page shows how far the real fleet sits below it.

**Minute 0 to 1, the headline.**

- The bare address: the tab "What a battery earns" is the third of three; "Your battery" reads ERCOT, "4 hours", "Perfect foresight", 100.
- The sentence under "What did it earn?": "Over the last twelve months a 100 MW, 4-hour battery in ERCOT earned USD 81.40 per kW, 33 percent of it from ancillary services, and covered its debt 2.63 times."
- "Last twelve months, all streams": USD 81.40 per kW; USD 8.14 million (8,140,219) for 100 MW, October 2025 to September 2026. "A bad month": USD 475,477, December 2024. "Debt coverage": 2.63 times on USD 2.26 million (2,261,119) a year.

**Minute 1 to 2, the chart and the table.**

- "Revenue by year, USD per kW": 244, 402, 187, 2021 broken at the top (3,431), 393, 530, 148, 87, and 2026 hatched with "9 months" at 60.
- The line under the chart: "This is an upper bound: before 2024 it is mostly payment for holding reserves, to a battery longer than any Texas then had, and 2021 is one week of February. Recent years are the ones to read."
- "Income by stream", "Total, USD per kW": 81.40, 255.08, 614.58, 269.68 ("Without Feb 2021").
- The line under the table: "this model takes USD 2.25 per kW a month; ERCOT's storage resources were awarded USD 0.40 per kW of their power a month; the model is 5.66 times the awards."

**Minute 2 to 3, the other strategy, the other grid.**

- "Day-ahead schedule", "Show" (`?grid=ercot&dur=4&strat=dayahead&mw=100`): USD 73.00 per kW; 35 percent from ancillary services; coverage 2.26.
- "CAISO", "Show" (`?grid=caiso&dur=4&strat=dayahead&mw=100`): USD 64.96 per kW; 51 percent; 1.90. With "Perfect foresight": 79.05.
- The bad month's note ends ": CAISO is held from September 2024"; the second column reads "not held: CAISO holds one full year (2025)"; "Capacity" reads "Not held: California's resource adequacy prices are contract statistics, not yet in the warehouse".
- The line under the income table: "In 2025, for a 4-hour battery on the day-ahead schedule, this model takes USD 42.31 per kW from energy and USD 42.25 from regulation; CAISO's market monitor reports that real batteries in its area with a full year of operation earned about USD 35 per kW from energy and USD 9 from regulation", then (session 263) "The two differ in regulation: this model sells it as if the market had no size, and the monitor writes that ...". The line is always the 4-hour battery on the day-ahead schedule, and says so.
- The line that begins "Every month, CSV" ends with the stress days, the days of CAISO's system-wide notices (4 to 9 September 2024, 20 and 21 January 2025, 9 and 10 September 2026, 5 to 8 October 2026). ERCOT's reads "Uri, Elliott, the 2023 heat".

**Minute 3 to 4, is it worth building.**

- Scenario A at the bare address: revenue USD 81.40; coverage 2.63; NPV USD -69.78 million (USD -697.80 per kW at 12 percent); IRR -8.8 percent; toll USD 4.19; merchant tail USD 0 (0 years).
- Type 50 into "Contract share" and 10 into "Contract price" (`?an=50&ap=10`): the headline sentence gains "with 50 percent of its power contracted at USD 10 per kW-month,", coverage 3.48; NPV USD -51.13 million.
- "Reset all of A", then 620 into "Capital cost" (`?ac=620`): NPV USD -23.12 million, IRR 2.1 percent.
- Type 99999 into "Capital cost" (session 263): the field's note says "99,999 was typed: the field runs from 0 to 10,000, so 10,000 is used."

**Minute 4 to 5, what matters most.**

- "How far each assumption moves NPV, scenario A": ten rows at the defaults (twelve with a contract).
- The first two rows: "Cycles a day, at most" (USD 11.14 million, the move down to 0.5 cycles; the move up to 1.5 is USD 1.40 million) and "Capital cost" (USD 9.52 million either way for USD 100 per kW).
- Close on the source line: "Checked against: 15 published figures" (session 297), with "Each comparison, with its gap and the reason".
- A sixth minute: "Scenario B", efficiency 92, cycles 2: B's revenue USD 88.24 per kW against A's 81.40; "What differs" says so; "Copy A to B" undoes it.

**If something goes wrong.**

- "This tool is in review and will open when it is approved.": the internal view is not open. Open the unlock address again.
- "The table could not be read, so no number is shown": the live set did not answer. Reload.
- "Duration" acts at once (links, not part of "Show"); a change of duration drops a typed capital cost and fixed O&M.
- The numbers hold until October 2026 is complete in the table (about the first days of November); then every headline number moves, and `site/scripts/check-battery-figures.mjs` fails until this pack and `docs/methods/battery_earns_algorithm.md`, section 11.2, are updated.
- Only 86 and 1 offered under efficiency and cycles: the file of steps is withdrawn until the data machine's daily run rebuilds it; the line under the assumptions says which.

## Where every number comes from

| Number | File | Section |
|---|---|---|
| 81.40; 33 percent; 8,140,219; 475,477 (December 2024, 36 months) | `docs/methods/battery_earns_algorithm.md` | "The default case"; 4.2; 4.3; 11.2 |
| 2,261,119; 2.63; NPV -69.78 million (-697.80 per kW); IRR -8.8; toll 4.19 | the same | "Session 208"; 11.1; 11.2 |
| 255.08; 614.58; 269.68; 57 percent | the same | 4.5; 11.2 |
| 73.00; 35; 2.26; 79.05; 64.96; 51; 1.90; 3.48; -51.13; -23.12; 2.1; 3.02; 11.14; 1.40; 9.52; 88.24; 83.57; the first two rows | the same; `site/scripts/check-battery-figures.mjs` | 11.2 |
| 2.25; 0.40; 5.66; 142, 21.6, 122 and 4.4 percent; 17,180 to 21,365 MW | the same, and `site/data/battery_awards_beside.json` | 9 |
| 0.464; 1.29 and 1.6 percent; 0.023; 0.983; 2025-01-04; 1,096 days; 3.2e-10; 0.038 | the same | 3.3; 5; 3.4; 8 |
| Modo 55, 26.0, 29.4; E3 127, 475; Tyba 2.13, 6.19, 7.3; Lazard 144.90 to 320.04; ATB 44.40, 15 years; ICE 23.97; Potomac; 444, 888, 190 | the same | "Cross-checks" |
| The chart's years (243.7, 402.2, 187.5, 3,430.6, 393.1, 530.1, 147.7, 87.4, 60.2); 4.52 and 5.92; 69 to 82; 2.6, 9, 13 percent; 401.8, 562.3 | `docs/methods/battery_stack.md` | "How it differs"; "The fleet-limited estimate"; "Reserves that are called" |
| 84.72; 77.3; the quarters; 41.89, 42.83, 39; 85.34; 0.77; 91.74; 42.31; 42.25; 35; 9; 62.6, 64.2, 66.3, 111.7; 53, 78, 103; the monitor's words on regulation | the same, and `archive/sessions/SESSION_246_REPORT.md` | "CAISO beside its market monitor" |
| The 2025 ladder 87.4, 78.7, 46.2, 36.7, 28.5; 1.50 and 1.23 hours; 821 MW; 2,841.6; 10.0 percent | `docs/methods/battery_early_years.md` | "The ladder"; "What each step takes"; "February 2021" |
| 7.17, 4.17, 3.00, 18.81; 28.27, 44.29, 227 of 291 | `docs/methods/ercot_storage_realtime.md` | "As built on 5 October 2026" |
| 30.14; 6.53; 23.61; 9.70; -0.62; 14.53 | `docs/methods/ercot_storage_dam_offers.md` | "The gap in three parts" |
| California's line, its words, 35 and 9; the stress days | `site/lib/batterystack.ts`; `archive/sessions/SESSION_257_REPORT.md` | `FLEET_BESIDE`, `STRESS_BY`; "What to review" |
| ORDC adders end 2025-12-04 | `docs/methods/ercot_rt_price_adders.md` | "What it is" |
| Part 8's values | `site/public/battery/erw_2026_battery_replication.py` on `erw_2026_battery_dispatch.csv`; `runs/session263/compare.mjs` | part 8 |
| Part 5's months (February 2024 29 of 29; October 2026 12 of 31; CAISO April 2025 27 of 30) | `battery_stack_monthly`, read on 2026-10-14 by `runs/session263/months.mjs` | part 5 |
| Labels, addresses, defaults, bounds, steps, 1.25, the IRR bracket, the clamp lines | `site/app/cost-of-power/battery/` (`page.tsx`, `BatteryForm.tsx`, `Scenarios.tsx`), `site/lib/batterystack.ts`, `site/lib/battery/finance.ts` | the code |
| 254 of 254 (check-values in sessions 208 and 211) | `archive/sessions/SESSION_208_REPORT.md`, `SESSION_211_REPORT.md` | "Checks" |
