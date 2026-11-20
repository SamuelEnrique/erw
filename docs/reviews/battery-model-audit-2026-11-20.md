# What a battery earns: the model audited as a hostile expert would

Session 9840, 20 November 2026, the desktop's fifth window. Read as a storage developer's quantitative analyst who wants to find it wrong.

- The page: `/cost-of-power/battery`. The model: `warehouse/derived/battery_stack.py`. The page's arithmetic: `site/lib/batterystack.ts`, `site/lib/battery/finance.ts`.
- The notes: `docs/methods/battery_earns_algorithm.md` ("the note"), `docs/methods/battery_stack.md`, `docs/methods/crosschecks/battery.md`. The replication: `replication/battery/`. The decisions block: `site/lib/decisions.ts`, `BATTERY_DECISIONS` (the note's section 12).
- Nothing changed on main but this file. No table written, no lock taken, no default moved.
- Each finding's test is on its own branch, `wip/audit-battery-<n>`, not requested for landing: a fix that moves a figure is the owner's ruling.

## In short

- **The arithmetic is right.** Every figure the page prints follows from the model's monthly table as the note says, and the model, re-solved from the page's own prices, gives 81.4022 per kW for the page's window. Nothing double counts a megawatt.
- **The model's rules are not what the page says they are.** "Each figure is an upper bound" is false: two of the model's own rules (an empty battery each midnight, the hourly mean of a 15-minute price) hold it 8.3 percent under a foreseeing battery's 88.81 per kW (findings 2, 3, 6). "Reserves are never called" is false for regulation: ERCOT's storage shows 17 percent of an award moving each hour, worth -7.9 percent (finding 1). At the default the biases roughly cancel (83.02 with all three).
- **The page's words and its figures disagree twice more.** The "Breakeven toll" covers debt 1.25 times and leaves equity worse off than merchant (finding 5). "4 hours at rated power" is 3.71 hours in the model (finding 10).
- **The finance leaves out what a developer's NPV holds.** No tax and no depreciation against an after-tax rate (+118.95 per kW; +426.14 with the 30 percent credit, finding 8), two kinds of dollars in one sum (+40 to +61, finding 9), degradation cut one for one with capacity where the model's own runs lose less than half of that (+44.76, finding 4).
- **Size.** Past about 500 MW the battery is paid for reserves ERCOT does not buy (finding 7).
- **Wording fixes are on branches 5, 6 and 10** and move no figure. Every other fix moves figures and is the owner's ruling; each finding has a test on its own branch.

## How every number here was computed

- The default case: ERCOT, 4 hours, perfect foresight, 100 MW. The page's last twelve months: October 2025 to September 2026. Headline USD 81.40 per kW (81.4022 unrounded).
- Prices: the page's own public file, `site/public/battery/erw_2026_battery_dispatch.csv`, 1,096 local days.
- Re-solved with the model's own `solve_day` and `check_day`: every day equals the file to 0.000000 USD per MW. The last twelve months give 81.4022.
- To change one rule at a time: a sparse restatement of the same program. With the model's rules it equals `solve_day` on all 365 days of the last twelve months, to 0.000000.
- 15-minute prices: `ercot_all_hub_prices_history`, then `iso_rtm_hub_prices` (HB_HUBAVG, the model's own order), read from the main checkout, never written. Their hourly means equal the file's energy price in all 8,760 hours.
- Regulation called: measured in `ercot_sced_esr_hourly` (ERCOT's 60-day SCED storage data, 1 February to 27 August 2026).
- Finance: a mirror of `finance.ts`. It gives the page's NPV (USD -697.80 per kW), IRR (-8.8 percent), coverage (2.63) and toll (4.19).
- A change of USD 1 per kW a year in revenue moves the default NPV by USD 6.43 per kW (twenty years at 12 percent, 2.6 percent degradation).

## Findings, largest effect first

| # | Finding | Headline, USD per kW (81.40) | NPV, USD per kW (-697.80) | Branch |
|---|---|---|---|---|
| 8 | The NPV holds no tax, no depreciation, and by default no credit, yet is discounted at a cost of equity | none | +118.95 after federal tax; +426.14 with the 30 percent credit as well | `wip/audit-battery-8` |
| 6 | "Each figure is an upper bound" is false: findings 2 and 3 together give 88.81; with finding 1 as well, 83.02 | the bound: +7.41 (+9.1 percent) | +47.6 | `wip/audit-battery-6` (fix in words) |
| 4 | Degradation cuts the whole revenue 2.6 percent a year; the model's own runs lose 1.1 percent a year at that fade | none (year 1) | +44.76 | `wip/audit-battery-4` |
| 1 | Regulation is never called; ERCOT's storage shows 17 percent of an award moving each hour | -6.44 (-7.9 percent) | -41.4 | `wip/audit-battery-1` |
| 9 | Flat real revenue, a fixed money debt payment and a money discount rate in one sum | none | +39.67 to +60.95 (inflation 2 to 2.5 percent) | `wip/audit-battery-9` |
| 2 | Each day starts empty: the reset costs USD 5.23 per kW, four times the note's bound of 1.29 | +5.23 (+6.4 percent) | +33.6 | `wip/audit-battery-2` |
| 10 | "A 4-hour battery discharges at its rated power for 4 hours": in the model it delivers 3.71 MWh per MW | +2.60 (+3.2 percent) if read as the page says | +16.7 | `wip/audit-battery-10` (fix in words) |
| 3 | Energy is paid the hourly mean; ERCOT settles real-time energy every 15 minutes | +2.23 (+2.7 percent) | +14.4 | `wip/audit-battery-3` |
| 5 | The "Breakeven toll" (USD 4.19 per kW-month) only covers debt 1.25 times; equity breaks even at 13.62 | the toll figure: 4.19 against 13.62 | at the 4.19 toll: -845.78 | `wip/audit-battery-5` (fix in words) |
| 7 | The size runs to 5,000 MW and scales linearly; past about 500 MW the battery is paid for reserves ERCOT never buys | none at 100 MW; -27.0 percent of revenue at 5,000 MW (September 2026) | none at 100 MW | `wip/audit-battery-7` |

| 11 | The public file, the replication and the note's section 11.2 prove October 2025 to September 2026; the table has moved to November to October | the default's headline in the table: 80.34, not 81.40 | | `wip/audit-battery-11` |

- Ranked by how far the default case's NPV moves, per kW (the smaller end of a range). Finding 11 is about what the replication proves, not about the model, and comes last. Finding 6 is findings 2 and 3 together. Finding 5 moves a printed figure, not NPV. Finding 7 moves nothing at the default 100 MW.

## 1. Regulation is never called

- **Where.** `warehouse/derived/battery_stack.py` line 28 (the docstring), lines 211 to 217 (the state of charge moves only with charge and discharge), line 267 (the objective pays an award its price, nothing else). The note, section 3.4 ("Reserves are never deployed"), section 4.11 and section 6 ("Reserves called: never, assumed"). Decision 4 (`site/lib/decisions.ts` line 119).
- **Why it is wrong.** ERCOT deploys regulation all the time. In `ercot_sced_esr_hourly`, over the 56,845 resource-hours in which a storage resource held regulation and no other reserve, its output moved off its base point by 0.168 MWh per MW of Reg Up and 0.181 per MW of Reg Down, net within each hour (least squares). Hours with no reserve moved about a sixth as much (mean 0.54 MWh against 3.20).
- **The other reserves are not called, as the model assumes.** In hours holding RRS, ECRS or Non-Spin alone, output moved off its base point about as much as in hours with no reserve: mean 0.37 to 0.99 MWh against 0.54, 2 to 6 percent of the award. The fault is regulation's alone.
- **The model leans on regulation.** In the mean hour of January to July 2026 it holds 44.6 percent of its power in Reg Up and 77.7 percent in Reg Down: 122 percent of its power in regulation.
- **The schedule it is paid for cannot be delivered.** Take `solve_day`'s own schedule and call regulation at 17 percent: on 342 of the 365 days the model's own `check_day` finds a limit broken (empty, full, or the energy behind a reserve).
- **How much.** Re-optimized with regulation called (the energy paid at the hour's price, the round-trip loss on it, Reg Up's energy counted in the one-cycle limit): USD 74.96 per kW, -6.44 (-7.9 percent). Of that, -3.93 is the energy and its losses and -2.51 the cycle limit. Called at 10 percent: 76.09; at 30 percent: 74.06. The battery then holds Reg Up 0.09 and Reg Down 0.35 MW per MW, not 0.47 and 0.76.
- **The test.** `tests/test_audit_battery_1.py` on `wip/audit-battery-1`: the paid schedule of every day of the last twelve months, with regulation called at 0.17, breaks `check_day` on at least 300 days (342 measured). On a machine with the SCED table it measures the share again (between 0.10 and 0.25).
- **Not fixed.** The fix is a model change (an energy flow per regulation award in the state of charge, the objective and the cycle row) and moves every figure: the owner's ruling. The measurement is real-time telemetry under ERCOT's real-time co-optimization (from 5 December 2025); the deployed energy is priced here at the hour's mean real-time price.

## 2. Each day starts empty, and the cost is four times what the note says

- **Where.** `warehouse/derived/battery_stack.py` lines 211 to 217 (`soc_row(-1)` is an empty battery at every day's first hour) and line 405 (each local day solved alone). The note, section 3.4 line 81 ("`s = 0` at the start of every local day"), section 5 lines 229 and 230, section 6 line 246. Decision 2 (`site/lib/decisions.ts` line 114).
- **What the note claims.** Section 5: the empty start "understates the result: at most USD 1.29 per kW over the last twelve months" (1 MW of the best-paid upward product in every first hour), and energy left at midnight is small (mean 0.023 MWh per MW). Both figures check: 1.2877 and 0.0227.
- **Why the bound is wrong.** It counts one channel, the first hour's reserves. The reset also stops the battery from charging before midnight for the next morning's peak, and from carrying stored energy behind overnight reserves. Winter, with two peaks a day, shows it most: December 2025 gains 11.6 percent, January 2026 9.3 percent.
- **How much.** The model's program with the state of charge carried across midnight within each calendar month, every other rule unchanged (one cycle per local day, 86 percent, hourly, the day's required durations): USD 86.63 per kW against 81.40, +5.23 (+6.4 percent). Carried across every midnight of the twelve months (one program of 8,760 hours): 86.93, +5.53 (+6.8 percent).
- **The test.** `tests/test_audit_battery_2.py` on `wip/audit-battery-2`, with `tests/audit_battery_lp.py` (the restated program). It shows the restatement equals `solve_day` on all 365 days, gives the page's 81.4022, then finds the carried figure more than four times the note's bound above it.
- **Not fixed.** A carried state of charge is a model change that moves every figure: the owner's ruling. The note's section 5 sentence is wrong as written whatever the ruling, and can be corrected in words.

## 3. Energy is paid the hourly mean of a price ERCOT settles every 15 minutes

- **Where.** `warehouse/derived/cost_of_power.py` lines 72 to 80 (`hourly`: the four quarter prices of an hour become their mean), used by `warehouse/derived/battery_stack.py` lines 358 and 360. The note, section 3.1 line 48, section 4.11 line 213, section 6 line 247 ("Resolution: hourly, as ancillary prices are hourly"). Decision 3 ("paid the hourly mean of the real-time price").
- **Why it is wrong for an upper bound.** ERCOT settles real-time energy on 15-minute settlement point prices. A battery under perfect foresight can charge in a cheap quarter and discharge in a dear one inside the same hour; the mean hides that spread. Reserves are bought by the hour, so they can stay hourly; energy need not.
- **What the note says.** Section 4.11 admits it in words ("can earn more from energy than this shows"), yet decision 3 still calls each figure an upper bound.
- **How much.** The same program with the four quarter prices of each hour, reserves hourly, every other rule the model's (the midnight reset included): USD 83.64 per kW, +2.23 (+2.7 percent). Energy rises from 54.60 to 57.57 (+5.5 percent); reserves give a little back.
- **The test.** `tests/test_audit_battery_3.py` on `wip/audit-battery-3`. A day whose hours all have the same mean but whose quarters move: `solve_day` earns nothing from energy, the quarter-priced program earns from the spread. On a machine with ERCOT's 15-minute tables it also recomputes the last twelve months (the quarters' means checked equal to the public file in every hour).
- **Not fixed.** A 15-minute energy program moves every figure: the owner's ruling. The day-ahead schedule is hourly by ERCOT's own design and is not affected.

## 4. Degradation cuts the whole revenue by a capacity fade rate

- **Where.** `site/lib/battery/finance.ts` lines 213 to 221 (`revenueInYear`: `R x (1 - deg)^(t - 1)`, and under the fade method `R x (1 - fade)^k`). The note, section 11.1 line 385 (the default, 2.6) and line 417 ("Revenue in year t"), line 451 (the fade method: "revenue is taken proportional to the capacity"). Decision 15 (`site/lib/decisions.ts` line 140).
- **Why it is wrong.** Lazard's 2.6 percent is the battery's loss of energy capacity a year. Power does not fade, a third of the revenue is reserves paid on power, and energy arbitrage is not proportional to the hours held. The note itself says "revenue is not proportional to duration" (section 11), then applies the fade one for one, under both methods.
- **What the model says instead.** Re-solved by `solve_day` on every day of the last twelve months, keeping 1 MW and fading the energy by 2.6 percent a year: year 2 earns 98.91 percent of year 1, year 10 90.26, year 20 79.34. The page's cut gives 97.40, 78.89 and 60.62.
- **How much.** The headline (year 1) does not move. NPV at the defaults: USD -653.04 per kW on the model's own fade path against -697.80, +44.76 per kW (USD 4.48 million for 100 MW). Twenty years of revenue: 1,459 per kW against 1,282 (+14 percent).
- **The test.** `tests/test_audit_battery_4.py` on `wip/audit-battery-4`: the faded battery keeps more than 98.5 percent of its revenue after one year and more than 75 percent after nineteen, while `finance.ts` (run by Node) gives `R x 0.974^(t - 1)` under both methods.
- **Not fixed.** The fix is a fade path from the model (a table of revenue by faded duration, or a ratio the page reads) and moves NPV, IRR and payback: the owner's ruling. The same path would make the augmentation option's revenue right.

## 5. The "Breakeven toll" is not a breakeven

- **Where.** `site/lib/battery/finance.ts` lines 283 to 289 (`breakevenToll`: `(1.25 x debt + fom) / 12`), the label in `site/lib/battery/view.ts` line 29 and `site/app/cost-of-power/battery/Scenarios.tsx` lines 187 and 377. The note, section 11.1 line 423, and the cross-check row of line 563, which sets this toll beside Lazard's levelized cost of storage.
- **Why it is wrong.** The figure is the toll at which debt is covered 1.25 times: it sizes the lender's loan. At 20 percent debt it is small, and it says nothing about whether the owner breaks even. "Breakeven" reads as the price at which the battery pays for itself.
- **How much.** Default case: the page prints USD 4.19 per kW-month. With the page's own contract arithmetic (the whole battery tolled at that price for the debt's 20 years), equity's NPV at 12 percent is USD -845.78 per kW (USD -84.58 million for 100 MW), worse than the merchant case's -697.80. The toll at which equity's NPV is zero is USD 13.62 per kW-month: the page's figure is 31 percent of it.
- **The test.** `tests/test_audit_battery_5.py` on `wip/audit-battery-5`. Through `finance.ts` (run by Node): the toll is 4.19, NPV at it -845.78, below merchant, and the zero-NPV toll 13.62 (passes on main). The label test fails on main and passes on the branch.
- **The fix on the branch.** In words only, no figure moves: the label becomes "Toll for 1.25 times coverage" in `view.ts` and `Scenarios.tsx`; `tests/test_session296.py` follows; the note's line 423 says what the figure is and is not, with the two figures above. Whether to add the zero-NPV toll as a figure is the owner's ruling.
- **The sister page already does it.** The generator page labels the same arithmetic "Contract price at which coverage reaches 1.25 times" (`site/app/cost-of-power/seller/SellerScenarios.tsx` line 248) and keeps "Breakeven" for the price at which NPV is zero (line 257, `breakevenPpa` in `site/lib/seller/finance.ts`). On the battery page the same word means the other figure. (Corrected: this finding said at first that the generator page carries the same label; it does not.)

## 6. "Each figure is an upper bound" is false

- **Where.** Decision 3 (`site/lib/decisions.ts` line 117, the note's section 12 item 3): "so each figure is an upper bound". The year chart's sentence (`site/app/cost-of-power/battery/page.tsx` lines 177 and 178: "This is an upper bound"), the strategy line (line 181) and its hover (`BatteryForm.tsx` line 16). The note, section 4.11 line 212. The dispatch file's header (`warehouse/derived/battery_dispatch_export.py` line 260).
- **Why it is false.** Findings 2 and 3 are rules that hold the figure below what a battery that foresaw the prices could earn under every other rule of the model. A bound has to sit above everything it bounds.
- **How much.** On the default case's last twelve months, 15-minute energy and the charge carried across midnight, together: USD 88.81 per kW against 81.40, +7.41 (+9.1 percent). The page's figure is 8.3 percent under that bound.
- **It is not a lower bound either.** Add finding 1 (regulation called at the measured 17 percent) to the same program: 83.02, +1.61 (+2.0 percent). The biases roughly cancel at the default; perfect foresight, a price taker and the hub still push it above what an operator gets. The honest word is "optimistic", not "upper bound".
- **The test.** `tests/test_audit_battery_6.py` on `wip/audit-battery-6`. December 2025 from the public file: the carried program (checked equal to `solve_day` on each day) earns 11.6 percent more than the model's days; quarter prices inside flat hours pay. Both pass on main. A third test, that no page text or decision says "upper bound", fails on main and passes on the branch.
- **The fix on the branch.** Words only, no figure moves: decision 3 and the note's section 12 (kept word for word, `tests/test_session5001.py` passes), the chart's two sentences ("This is optimistic, not an upper bound: ..."), the strategy line and hover, the note's section 4.11. `tests/test_session102.py` and `site/scripts/test-battery-stack.mjs` follow; the second needs the built site and was not run here.

## 7. The size field pays for reserves ERCOT never buys

- **Where.** `site/lib/batterystack.ts` line 106 (`mw` from 1 to 5,000) and line 447 (`scaled`: every dollar figure is the per-MW figure times the size), read by the headline's "USD for the reader's size". The note, section 2 line 28, section 4.11 line 208 ("large sizes are overstated, ancillary income most of all"), section 6 line 249 ("Price taker: assumed"). Decision 4.
- **Why it is wrong.** A price taker is a fair assumption for one battery that is small beside the market. ERCOT buys a fixed quantity of each reserve: in September 2026 its day-ahead plan held a median of 387 MW of Reg Up and 393 MW of Reg Down (`ercot_as_quantities`). At 100 MW the model already holds 57 and 78 MW of them in the mean hour, 15 and 20 percent of the whole market. The page says large sizes are overstated, then prints them scaled.
- **How much.** The 672 hours of September 2026 both tables hold, the model's own hourly awards times the size, against ERCOT's plan hour by hour:
  - 100 MW: never above ERCOT's purchase. No effect at the default.
  - 500 MW: Reg Down above ERCOT's whole purchase in 47 percent of hours; 2.7 percent of the hours' revenue is for megawatts ERCOT does not buy.
  - 1,000 MW: 79 percent of hours; 10.8 percent of revenue.
  - 5,000 MW: 83 percent of hours; 27.0 percent of revenue (USD 8.0 million of 29.6 million in that month), 89 percent of the regulation revenue.
- **The test.** `tests/test_audit_battery_7.py` on `wip/audit-battery-7`: the page's library (run by Node) reads 5,000 MW and scales the twelve months by exactly 50; the public file's September 2026 awards at 5,000 MW sit above ERCOT's plan in most hours and more than a fifth of the revenue is for megawatts never bought. It reads `ercot_as_quantities` where it is on the machine, else the figures read here.
- **Not fixed.** Lowering the size's bound, or a line when the awards outgrow the market, is the owner's ruling. ERCOT's plan is held for 40 days only (from 3 September 2026), so a check across the twelve months needs its history.

## 8. The NPV holds no tax at all

- **Where.** `site/lib/battery/finance.ts` lines 243 to 248 (`flows`: no tax term; the credit is added at year 0 with no basis cut) and line 104 (`defaultsOf`: `itc: 0`). The note, section 11.1 line 418 ("No tax, no tax credit, ..."), line 450 (the credit) and line 467 ("What this block is not"). Decision 16 (`site/lib/decisions.ts` line 142).
- **Why it is wrong.** The rate that discounts the flows is a cost of equity, 12 percent, which is a return after tax. The flows it discounts are before tax: no income tax, no depreciation. And the page's own hover names the federal credit for storage (30 percent before bonuses) while the default takes none, so every NPV on the page assumes the owner forgoes it. Stated in the note, but wrong in kind for a developer's NPV.
- **How much.** The default case after federal tax (21 percent; 5-year MACRS, half-year convention; the basis cut by half the credit; interest deductible; losses used as they arise), every other figure the page's:
  - no credit: USD -578.85 per kW against -697.80, +118.95 (USD 11.9 million for 100 MW);
  - with the 30 percent credit: -271.66, +426.14;
  - the page's own credit field (no tax): -364.80, +333.00.
  - The headline revenue and coverage do not move.
- **The test.** `tests/test_audit_battery_8.py` on `wip/audit-battery-8`: through `finance.ts` (run by Node) the default credit is 0 and a 30 percent credit moves NPV by exactly 30 percent of the capital cost (no tax term); the same case after tax gives -578.85 and -271.66.
- **Not fixed.** Tax, depreciation and the credit's default are the owner's ruling. Eligibility for the credit (wages, sourcing rules) is the project's; the figures above only show what the choice is worth.

## 9. Two kinds of dollars in one sum

- **Where.** `site/lib/battery/finance.ts` lines 206 (`debtService`, a level payment at the interest rate), 213 to 221 (revenue flat apart from degradation) and 243 to 255 (`flows` and `npv` at the hurdle rate). The note, section 11.1 line 418 ("revenue and costs are flat in today's dollars apart from degradation").
- **Why it is wrong.** Revenue and fixed O&M are flat in today's dollars: a real convention. The debt payment is a level payment on an 8 percent loan: fixed in money, so in real terms it shrinks each year. The 12 percent hurdle is a money rate. A real flow wants a real rate; a money payment wants money flows. Mixing them counts inflation against the owner twice.
- **How much.** Either consistent reading raises the default NPV (USD -697.80 per kW):
  - money flows (revenue and O&M rising with inflation, the debt fixed) at 12 percent: -658.13 at 2 percent inflation (+39.67), -647.10 at 2.5 (+50.70);
  - real flows (the debt deflated) at the real rate (9.80 and 9.27 percent): -650.15 (+47.65) and -636.85 (+60.95).
  - The inflation rate is this audit's assumption, not a source's: 2 and 2.5 percent bracket the usual planning figures. The headline revenue and coverage do not move.
- **The test.** `tests/test_audit_battery_9.py` on `wip/audit-battery-9`: through `finance.ts` (run by Node) the debt payment is one number every year while income falls by the degradation alone; both consistent readings give the four figures above.
- **Not fixed.** An inflation rate is a new assumption: the owner's ruling. The smallest fix in words is to say in the note which dollars the 12 percent is in.

## 10. What "4 hours" means: the page and the model disagree

- **Where.** `warehouse/derived/battery_stack.py` lines 219 to 225 (`s <= D`, the energy stored) with discharge at `1 / eta`. The page: `site/app/cost-of-power/battery/BatteryForm.tsx` line 64 (the hover: "How long the battery can discharge at its rated power: a 4-hour battery holds 4 MWh for each MW") and line 68 (the link title: "discharges at its rated power for 4 hours, 4 MWh for each MW"). The note, section 3.4 line 81, states `0 <= s_t <= D` and never says which side of the losses `D` is on.
- **Why it is wrong.** In the model a full 4-hour battery delivers `4 x sqrt(0.86)` = 3.71 MWh per MW: it holds its rated power for 3.71 hours, not 4. It also needs 4.31 hours at rated power to fill. The page's words describe a different battery.
- **Which reading is right is a convention.** Lazard's 4-hour case delivers about 3.6 MWh per MW a cycle (90 percent depth of discharge: 126,000 MWh a year over 350 cycles for 100 MW, the note's own cross-check row); the ATB's 4 hours are 4 hours of rated output. The model sits between them. The fault is that the page says one thing and computes another.
- **How much.** Read as the page says (4 MWh delivered from full, so `4 / eta` stored), the default case's last twelve months: USD 84.01 per kW against 81.40, +2.60 (+3.2 percent).
- **The test.** `tests/test_audit_battery_10.py` on `wip/audit-battery-10`: on a day that fills and empties the battery, `solve_day` delivers exactly `D x sqrt(0.86)` at 2, 4 and 8 hours, and no day of the public file delivers more than 3.7094 MWh per MW (passes on main). The words test fails on main and passes on the branch.
- **The fix on the branch.** Words only, no figure moves: the hover and the link titles say what is stored and what is delivered (3.71 MWh per MW at 4 hours, 1.85 at 2, 7.42 at 8), and the note's section 3.4 says what `D` is. Changing the model to the page's words would move every figure: the owner's ruling.

## 11. The replication proves a window the page has left

- **Where.** `replication/battery/page_figures.json` (its window: last twelve months October 2025 to September 2026) and `replicate.py` (it reads only the public file and that JSON); `site/public/battery/erw_2026_battery_dispatch.csv` (months 2023-10 to 2026-09). The note, section 7.1 ("On 6 November 2026: 22 of 22") and section 11.2 (the figures of 14 October, "when October 2026 is complete every one moves, and the script, this table and the pack change together").
- **Why it is wrong.** October 2026 is now whole in the table, so the page's last twelve months are November 2025 to October 2026. `replicate.py` compares the public file with the figures written for it, so it passes whatever the table says: it proves the arithmetic of a page that is no longer shown.
- **How much.** The table on the data machine (built 14 November) gives the default case USD 80.34 per kW over November 2025 to October 2026, against the replication's 81.40 (-1.06, -1.3 percent). Re-solved on today's prices, 80.40: the table's October holds one day fewer than the prices now do (CAISO's likewise, 30 days against 31).
- **The test.** `tests/test_audit_battery_11.py` on `wip/audit-battery-11`: `replicate.py` exits 0 on its own window (passes anywhere); on a machine with the table, the page's own rule applied to the table must give the replication's window. Run against the main checkout's table (read only) it fails: 2025-11 to 2026-10 against 2025-10 to 2026-09.
- **Not fixed.** Writing the public file and the page figures again is the data machine's (`warehouse/derived/battery_dispatch_export.py`, then the replication's JSON), outside this window's rules. Findings 1 to 10 hold on the new window (next section).

## The same checks on the other open cases

On the table's current last twelve months (November 2025 to October 2026), 4 hours, prices read from the main checkout through the model's own readers, the model re-solved to the table before any rule moved (the one month that differs, October 2026, by the day the table lacks, is taken as re-solved):

| Case | The table's twelve months, USD per kW | Carried across midnight (finding 2) | Regulation called at 17 percent (finding 1) |
|---|---|---|---|
| ERCOT, perfect foresight (the default) | 80.40 re-solved (table 80.34) | +5.58 (+6.9 percent) | -6.39 (-7.9 percent) |
| ERCOT, day-ahead schedule | 72.59 | +4.57 (+6.3 percent) | -6.41 (-8.8 percent) |
| CAISO, perfect foresight | 80.12 re-solved (table 79.80) | +6.06 (+7.6 percent) | -10.27 (-12.8 percent) |
| CAISO, day-ahead schedule | 65.96 | +4.46 (+6.8 percent) | -8.57 (-13.0 percent) |

- Both findings hold on every open case, in the same direction and about the same size; CAISO leans harder on regulation, so calling it costs more.
- CAISO's column applies ERCOT's measured 17 percent: no CAISO deployment is held, so it is a sensitivity, not a measure.

## What was checked and found right

- **The objective.** `solve_day` line 267: the cost of charging less the revenue of discharging and of each award. Energy at `p x (d - c)` (USD per MWh times MWh in an hour), each award at its price (USD per MW for the hour times MW). Right.
- **No megawatt paid twice.** `structure` lines 226 to 240: in each hour, discharge plus every upward award (Reg Up, RRS, ECRS, Non-Spin) is at most 1 MW, and charge plus Reg Down at most 1 MW. The four upward products share the one upward limit; Reg Down is the only downward one. `check_day` checks the same. If anything conservative: a charging battery could offer more upward (stop charging, then discharge), and the model does not credit it.
- **The state of charge and the round trip.** Charge times `eta`, discharge over `eta`, `eta = sqrt(0.86)`: 86 percent applied once, split evenly, on the right sides.
- **The energy behind a reserve.** Upward: `h / eta` MWh stored per MW (what delivering it draws). Reg Down: `h x eta` of room. Checked at the hour's start and end, which covers the hour, the state of charge moving in a straight line within it.
- **The required durations.** Taken on the day (`required_hours`): ERCOT 1 hour (assumed) to 4 December 2025, then 30 minutes, for Reg and RRS; ECRS 2 hours, then 1; Non-Spin 4 hours from 9 December 2022; ECRS no product before 10 June 2023. The code, the note and the page's table agree. ERCOT's rule texts were not read again here.
- **The cycle limit.** `sum d / eta <= D`: the energy taken out in a local day is at most one full charge; 0.983 cycles a day over the last twelve months.
- **Negative prices.** The charge-or-discharge switch in negative-price hours only. The netting at a price of zero or more keeps the state of charge and gains `p x b x (1 - eta^2)`, never less. 586 negative hours on 141 days; one switch day (4 January 2025); no negative reserve price.
- **Clock changes and timestamps.** Reserve prices: hour ending to hour start, the repeated autumn hour by ERCOT's flag (`warehouse/connectors/ercot_as_prices.py`, `to_utc`). Real-time prices: interval start, the flag likewise (`warehouse/connectors/ercot_zone_prices.py`, `interval_start`), so the hourly mean is of the hour's own quarters. `day_hours` gives 23, 24 or 25 hours. In the file the 25-hour days hold two distinct 01:00 hours with distinct prices, and the 23-hour days skip 02:00.
- **Missing hours.** A day missing any hour of any price bought that day is left out and counted, never filled or scaled (`build_market` lines 393 to 402). ERCOT: none left out.
- **Days to months to the headline.** Solved days summed, rounded to four decimals; a month counts at 90 percent of its days; the window is the newest twelve whole held months; per kW is per MW over 1,000; the size is a multiplication. The library (`lastTwelve`, `sumOf`, `badMonth`, `last36`, `coverage`) matches the note line by line, and the model re-solved gives 81.4022 for the page's window.
- **The bad month.** Nearest rank, `ceil(0.1 x n)` of the held months of the 36 ending with the window: rank 4 of 36.
- **The finance arithmetic.** `crf`, the level payment, coverage `(R - fom) / debt`, NPV, IRR by bisection, payback, the toll formula: a mirror gives -697.80 per kW, -8.81 percent, 2.6271 and 4.1887, as the page; the revenue for a zero NPV is 189.92 per kW a year, the note's "about 190".
- **Scenario A against B.** Each column takes its own assumptions and, at another step of efficiency or cycles, its own months from the file of steps (`revenueAt`, `useBlock`); A alone sets the headline (`useA`). A step is offered only while the file still describes the live months (`stepState`). The file of steps changes only the cycle row's bound (asserted) and must reproduce the table month by month.
- **The note's smaller claims.** 1.29 per kW (the first hour), 0.023 MWh left at midnight on 11 days, 142 percent of power in awards, 0.983 cycles: each recomputed from the file and right as stated. Finding 2 is about what the 1.29 claims to bound, not the figure.
- **The replication.** `replicate.py` redoes the page's arithmetic from the model's own output, and the optimizer check re-solves the same program another way. Both are sound for what they claim. Neither tests the model's rules; that is what this audit adds.

## Not covered, or left open

- **CAISO.** Findings 1 and 2 recomputed (the section above); the others not. Its regulation mileage payments are left out (an understatement), and its 25-hour days are left out because the hub history lacks them.
- **The day-ahead schedule.** Findings 1 and 2 recomputed for ERCOT and CAISO (above); finding 3 does not apply; finding 7 applies and was not recomputed.
- **Real-time reserve prices** since ERCOT's real-time co-optimization (5 December 2025): a foreseeing battery could also sell reserves in real time. Not modelled, not quantified: the reserve table holds day-ahead prices.
- **The stress repeats** add the peak event's whole window revenue on top of a normal year, so the window's ordinary days count twice: about USD 4 per kW of Uri's 3,105.51 (0.1 percent). Negligible.

## The deploys of this file (rule 8)

Every page is in review, so a visitor sees the in-review page at all 25 addresses; this file changes no page. Each push: `node site/scripts/snapshot-live.mjs take` before, the after once the Vercel deployment of a commit holding the push showed success, then `compare`.

- Push 1 (finding 1), merge `291223a4`; deployed in `194cf4c3`, success 21:08:35 UTC. `s9840-f1-before` against `s9840-f1-after`: 0 differences on 25 pages. Expected.
- Push 2 (findings 2 to 4), merge `fd3d8fd8`; success 21:14:18 UTC. `s9840-f2to4-before` against `s9840-f2to4-after`: 0 differences. Expected.
- Push 3 (finding 5), merge `0b89df07`; success about 21:19:26 UTC. `s9840-f5-before` against `s9840-f5-after`: 0 differences. Expected.
- Push 4 (findings 6 and 7), merge `63b4d0ec`; success about 21:24:48 UTC. `s9840-f6f7-before` against `s9840-f6f7-after`: 0 differences. Expected.
- Push 5 (findings 8 to 10), merge `7cf20b93`; success about 21:30:48 UTC. `s9840-f8to10-before` against `s9840-f8to10-after`: 0 differences. Expected.
- Push 6 (what was checked, not covered, the ranked table, the summary, finding 5 corrected), merge `ecb3bd89`; success about 21:35:51 UTC. `s9840-checked-before` against `s9840-checked-after`: 0 differences. Expected.
- Later pushes of this file ride with the generator audit's (session 9841); their snapshots are recorded in `docs/reviews/generator-model-audit-2026-11-20.md`.
