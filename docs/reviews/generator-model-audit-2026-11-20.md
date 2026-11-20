# What a generator earns: the model audited as a hostile expert would

Session 9841, 20 November 2026, the desktop's fifth window, after the battery page's audit (session 9840, `docs/reviews/battery-model-audit-2026-11-20.md`). Read as a developer's quantitative analyst who wants to find it wrong.

- The page: `/cost-of-power/seller`. The model: `warehouse/derived/merchant_revenue.py`. The page's arithmetic: `site/lib/merchant.ts`, `site/lib/seller2.ts`, `site/lib/seller/finance.ts`, `site/app/cost-of-power/seller/model.ts`.
- The note: `docs/methods/generator_earns_algorithm.md`. The decisions block: `site/lib/decisions.ts`, `GENERATOR_DECISIONS` (the note's section 13).
- Nothing changed on main but this file. No table written, no lock taken, no default moved.
- Each finding's test is on its own branch, `wip/audit-generator-<n>`, not requested for landing.

## In short

- **The revenue is sound.** The model reproduces from the page's own hourly file, the fleet's solar hours line up with the sun, and the two small faults found in it (selling below zero, the month-start nameplate) move the headline by less than 1 percent each, in opposite directions.
- **The finance carries the battery page's faults, larger.** No tax and no depreciation against an after-tax rate (+240.52 per kW of NPV, finding 1); two kinds of dollars over 35 years (+59.72 to +77.42, finding 2).
- **Two code faults in the contract and the credit.** An as-generated PPA is paid on energy the plant no longer makes, so the breakeven PPA price reads 58.36 where it is 61.50 per MWh (finding 4). The same tax credit lands a year later here than on the battery page (finding 3).
- **The battery on this page is called an upper bound and sits 2.1 percent under the battery page's own program on the same prices (finding 5).**
- **The note's table of defaults is two rulings out of date (finding 8, fixed in words on its branch).**
- **The peaker starts 403 times a year for free.** Its median run earns about USD 25 per MW, so any real start cost takes a large share of its margin: -14 to -36 percent at USD 25 to 100 per MW a start (finding 9).

## How every number here was computed

- The default case: ERCOT, solar, 100 MW, priced at the hub average in real time; the page's last twelve months, October 2025 to September 2026: USD 59.85 per kW, coverage 0.67 on debt payments of USD 7,078,769.
- Revenue: the page's own public file, `site/public/seller/erw_2026_generator_hourly.csv` (72,384 hours: price, the fleet's solar MWh, the month's nameplate). It gives 59.8523 per kW and 2,579.9 MWh per MW for the page's twelve months.
- The battery comparisons: the battery page's public file (`site/public/battery/erw_2026_battery_dispatch.csv`), whose hourly energy price is the same ERCOT hub average in real time.
- Finance: `site/lib/seller/finance.ts` run by Node in each test, and a mirror. Default case: NPV at 12 percent USD -766.62 per kW (USD -76.66 million for 100 MW), the breakeven PPA price USD 58.36 per MWh (the note's), the price for 1.25 times coverage USD 39.14 (the note's).
- A change of USD 1 per kW a year in revenue moves the default NPV by USD 7.76 per kW (35 years at 12 percent, 0.7 percent degradation).

## Findings, largest effect first

| # | Finding | Revenue, USD per kW (59.85) | NPV or price | Branch |
|---|---|---|---|---|
| 1 | The NPV holds no tax and no depreciation, yet is discounted at a cost of equity | none | NPV +240.52 per kW after federal tax | `wip/audit-generator-1` |
| 2 | Flat real flows, a fixed money debt payment and a money discount rate in one sum | none | NPV +59.72 to +77.42 per kW (inflation 2 to 2.5 percent) | `wip/audit-generator-2` |
| 3 | The same tax credit arrives in year 1 here and at year 0 on the battery page | none | a 30 percent credit on USD 1,110: 297.32 here, 333.00 there | `wip/audit-generator-3` |
| 4 | An as-generated PPA is paid on energy the plant no longer makes | none | breakeven PPA 58.36 against 61.50 per MWh | `wip/audit-generator-4` |
| 5 | The page's battery is "an upper bound", yet earns less than the battery page's program on the same prices | battery: -1.23 (-2.1 percent) at 4 hours | battery: NPV -7.9 per kW | `wip/audit-generator-5` |
| 6 | The merchant plant sells below zero, where a merchant plant would stop | +0.41 (+0.7 percent) if it stopped | NPV +3.2 per kW | `wip/audit-generator-6` |
| 7 | Output per MW is over the nameplate of the month's start, so new plants add output and not megawatts | -0.34 (-0.6 percent) at mid-month nameplate | NPV -2.6 per kW | `wip/audit-generator-7` (test with 6) |
| 8 | The note's table of defaults says hurdle 9.6 and solar degradation 0; the page uses 12 and 0.7 | none | none (words) | `wip/audit-generator-8` (fix in words) |
| 9 | The peaker starts 403 times a year with no start cost; the median run earns about USD 25 per MW | peaker margin 48.15: -14 to -36 percent at a start cost of USD 25 to 100 per MW | peaker NPV -53 to -138 per kW | `wip/audit-generator-9` |

## 1. The NPV holds no tax and no depreciation

- **Where.** `site/lib/seller/finance.ts` lines 241 to 247 (`flows`: no tax term), line 128 (`defaultsOf`: `itc: 0`, `ptc: 0`). The note, section 11.3 line 522 ("No tax, no tax credit, ..."), section 11.6 line 547. Decisions: "The NPV is discounted at 12 percent, Lazard's cost of equity" (`site/lib/decisions.ts` line 82) and the credits at 0 (line 98).
- **Why it is wrong.** A cost of equity is a return after tax; the flows it discounts are before tax, with no depreciation. The battery page's finding 8, on a plant whose capital is 1,375 per kW and 60 percent debt, so the interest and the depreciation weigh more.
- **How much.** The default case after federal tax (21 percent; 5-year MACRS, half-year convention; interest deductible on the level loan's schedule; losses used as they arise), every other figure the page's: NPV USD -526.10 per kW against -766.62, +240.52 (USD 24.1 million for 100 MW). Revenue and coverage do not move.
- **The credits.** The page's credit fields (investment and production) default to 0. Whether a new solar plant still qualifies (the credits' end dates and start-of-construction rules) is the project's; this audit does not claim it does.
- **The test.** `tests/test_audit_generator_1.py` on `wip/audit-generator-1`: through `finance.ts` the default holds no credit, the debt payment is 7,078,769 for 100 MW and NPV -766.62; after tax, -526.10.
- **Not fixed.** The owner's ruling, with the battery page's finding 8.

## 2. Two kinds of dollars in one sum

- **Where.** `site/lib/seller/finance.ts` lines 207 (`debtService`, a level payment), 214 (`revenueInYear`, flat apart from degradation), 241 to 254 (`flows`, `npv`). The note, section 11.3 line 522 ("no inflation").
- **Why it is wrong.** Revenue and fixed O&M are flat in today's dollars, the debt payment is fixed in money for 35 years, and 12 percent is a money rate. The battery page's finding 9, over a longer life.
- **How much.** Money flows (revenue and O&M rising with inflation, the debt fixed) at 12 percent: NPV USD -706.90 per kW at 2 percent inflation (+59.72) and -689.20 at 2.5 percent (+77.42). The inflation rate is this audit's assumption, not a source's.
- **The test.** `tests/test_audit_generator_2.py` on `wip/audit-generator-2`: the payment is one number in all 35 years and income falls by the degradation alone; the two money-flow NPVs.
- **Not fixed.** A new assumption: the owner's ruling.

## 3. The same tax credit, two different years

- **Where.** This page: `site/lib/seller/finance.ts` lines 236 and 237 (`creditInYear`: the investment credit in year 1) and its decision "the ITC arrives in year 1" (`site/lib/decisions.ts` line 98). The battery page: `site/lib/battery/finance.ts` line 245 (the credit in the year-0 flow, "taken at year 0 against the equity paid in", `battery_earns_algorithm.md` section 11.1 line 450).
- **Why it is wrong.** Section 11.1 of the battery note says the three pages share one scenario block. The same credit on the same battery is worth 12 percent less on this page.
- **How much.** A 30 percent credit on a 4-hour battery at USD 1,110 per kW: 333.00 per kW of NPV on the battery page, 297.32 here (-35.68). On this page's default solar plant at 1,375: 412.50 against 368.30 (-44.20).
- **The test.** `tests/test_audit_generator_3.py` on `wip/audit-generator-3`: both libraries (run by Node) with the same battery and a 30 percent credit; the battery page adds 333 to year 0, this page to year 1.
- **Not fixed.** Which year is right (when the credit is sold or used) is the owner's ruling; the two pages should agree.

## 4. An as-generated PPA is paid on energy the plant no longer makes

- **Where.** `site/lib/seller/finance.ts` lines 218 and 219 (`contractYear`: `cshare x cprice x energyKw`, with no year in it), used by `incomeInYear` (lines 231 and 232) for every year of the term, and by `breakevenPpa` (lines 314 to 322: one dollar of price is worth `E` MWh every year). Against line 214 (`revenueInYear`, degraded) and lines 236 and 237 (the production credit, degraded). The note, section 11.3 line 527.
- **Why it is wrong.** For the default shape, "generated", the contract buys the plant's output. Solar's output falls 0.7 percent a year (the page's own default since ruling 7a); by year 35 the plant makes 78.7 percent of year one's energy, and the contract is still paid on all of it. A block contract (fixed volume) is right not to degrade, and the code treats a block apart.
- **How much.** Default case, the whole energy for the PPA's 35 years: the breakeven PPA price the page prints, USD 58.36 per MWh, becomes 61.50 when the contract is paid on what the plant makes (+3.14, +5.4 percent). Every scenario with a contract overstates its contract income in the later years the same way.
- **The test.** `tests/test_audit_generator_4.py` on `wip/audit-generator-4`: through `finance.ts` the breakeven price is 58.36 and the contract income is the same in year 35 as in year 1; paid on the degrading volume, the zero-NPV price is 61.50.
- **The fix, not made.** `contractYear` takes the year and, for the "generated" shape, multiplies the energy by `(1 - deg)^(t - 1)`; `breakevenPpa`'s one-dollar value takes the same factor. It moves the breakeven price and every contract's NPV: the owner's ruling.

## 5. The page's battery is not an upper bound

- **Where.** `warehouse/derived/merchant_revenue.py` lines 136 to 171 (`battery_day`: in each hour full charge, full discharge or rest, with a last partial step) and lines 17 to 20 ("An upper bound: no one knows the day's prices in advance"). The note, section 3.3 line 81 ("an upper bound"). Decision 3 (`site/lib/decisions.ts` line 64: "so its figure is an upper bound").
- **Why it is wrong.** Full power or nothing is a restriction: a battery that foresaw the prices could also run at part power. The battery page's own program, with no reserve paid, has every other rule the same (86 percent, each day from empty, one cycle) and earns more. The battery audit's findings 2 and 3 (the midnight reset, the hourly mean) hold here too.
- **How much.** Every day of the last twelve months, the same ERCOT hub-average real-time prices: 4 hours, this page's program USD 58.72 per kW against the battery page's 59.95 (-1.23, -2.1 percent); 2 hours, 36.91 against 37.44 (-1.4 percent). The full-power program is below on 317 and 307 of 365 days.
- **The two pages disagree.** The same battery, the same prices, two answers: 58.72 here, 59.95 on the battery page's program without reserves.
- **The test.** `tests/test_audit_generator_5.py` on `wip/audit-generator-5`: a day where half power pays, and the twelve months at 4 hours (58.72 against 59.95, below on more than 300 days).
- **Not fixed.** Using the battery page's `solve_day` here moves the page's battery figures: the owner's ruling. The words "upper bound" can go now (the battery audit's finding 6 has the form).

## 6. The merchant plant sells below zero

- **Where.** `warehouse/derived/merchant_revenue.py` lines 268 to 274 (revenue is output times price over every hour with a value). The note, section 6 item 20 ("Solar and wind sell every hour, also at a negative price") and "What the model cannot see" ("no negative-price clause applies").
- **Why it is wrong.** A merchant plant with no production credit loses money on every MWh sold below zero and stops. The fleet's shape still sells there. Stated in the note; wrong for the plant the page says it models ("a merchant solar plant").
- **How much.** The page's twelve months: 189 negative hours, all with output; 117.7 MWh per MW sold below zero (4.6 percent of the year's energy) for USD -0.41 per kW. A plant that stops below zero: 60.26 per kW against 59.85 (+0.68 percent). It grows: -0.09 per kW in 2024, -0.31 in 2025, -0.32 in the nine months of 2026 held.
- **The test.** `tests/test_audit_generator_6.py` on `wip/audit-generator-6`: from the public hourly file, 59.8523, 189 hours, -0.4076, 60.2599.
- **Not fixed.** A curtailment rule moves the revenue: the owner's ruling. A plant that does take a production credit would sell down to minus the credit, which the page's credit field could set.

## 7. Output per MW over the nameplate of the month's start

- **Where.** `warehouse/derived/merchant_revenue.py` lines 111 to 115 (`capacity`: the nameplate operating on the month's first day) and lines 244 to 249 (output per MW = the fleet's generation over that figure for every hour of the month). The note, section 3.2 ("One figure a month"; "Nothing is trimmed").
- **Why it is wrong.** A plant that starts during the month adds its output to the numerator and not its megawatts to the denominator, so output per MW runs high while the fleet grows. ERCOT's solar grew from 28,045 to 32,760 MW over the page's twelve months; 184 of their hours sit above the nameplate (up to 1.075 MWh per MW).
- **How much.** With the month's mid-point nameplate (the mean of this month's start and the next month's): USD 59.51 per kW against 59.85 (-0.34, -0.6 percent). The capture price is not affected (it weighs by generation).
- **The test.** `tests/test_audit_generator_6.py` (the second test) on `wip/audit-generator-7`: 59.5086 at the mid-point nameplate, 184 hours above the nameplate, 28,045 to 32,760 MW.
- **Not fixed.** Which nameplate a month takes is the owner's ruling; the effect is small and states itself in the over-nameplate hours the page already counts.

## 8. The note's table of defaults is out of date

- **Where.** `docs/methods/generator_earns_algorithm.md`, section 11.1 lines 495 and 497: degradation "0; a battery 2.6", hurdle rate 9.6. The code: `site/lib/seller/finance.ts` line 76 (`HURDLE = 12`, session 208) and line 85 (`SOLAR_DEG = 0.7`, ruling 7a of 18 October 2026), used by `site/app/cost-of-power/seller/model.ts` line 148. The note's opening paragraph says 12 and section 7 says 0.7; the table, which a reader takes as the defaults, says neither.
- **How much.** No figure on the page; the note's worked NPV of section 11.4 (USD -78.43 million) is the 9.6 percent figure of sessions 196 to 207. At the page's defaults the NPV is USD -76.66 million (-766.62 per kW, finding 1's mirror).
- **The test.** `tests/test_audit_generator_8.py` on `wip/audit-generator-8`: the note's two rows against the two constants. Fails on main, passes on the branch.
- **The fix on the branch.** The two rows in words, with the rulings that set them.

## 9. The peaker starts for free

- **Where.** `warehouse/derived/merchant_revenue.py` lines 283 to 291 (run in every hour whose price is above Henry Hub times the heat rate plus variable O&M; the margin is the sum of price less cost over those hours) and lines 21 to 24 ("No start costs, minimum run, ramp limits, outages or gas basis"). The note, section 3.4 line 92. Decision 4 (`site/lib/decisions.ts` line 66).
- **Why it matters.** The rule takes every profitable hour as its own run. In ERCOT over the page's last twelve months it starts the plant 403 times for 1,772 run hours (4.4 hours a run); a quarter of the runs last one hour, and the median run earns about USD 25 per MW, the order of what a start costs a real peaker. Stated in the note, but not small.
- **How much.** The rule's margin, from the page's own snapshot arrays, is USD 48.15 per kW (the snapshot's rows: 48.1461). With a start cost per MW and the runs that would not pay their start skipped: USD 25: 41.55 (-13.7 percent, 203 starts); USD 50: 37.20 (-22.7 percent); USD 100: 31.01 (-35.6 percent). The start costs are this audit's sensitivity, not a source's; the page cites none. On the peaker's 30-year life at 12 percent, NPV moves by -53 to -138 per kW. 2024 and 2025 behave the same (502 and 411 starts).
- **The test.** `tests/test_audit_generator_9.py` on `wip/audit-generator-9`: from `site/data/merchant_snapshot.json`, the rule's margin equals the page's rows, 1,772 run hours, 403 starts, a quarter of them one hour long, a median run under USD 30 per MW, and more than a fifth of the margin gone at a start cost of USD 50.
- **Not fixed.** A start cost (and a minimum run) is a new assumption: the owner's ruling.

## The decisions block, line by line

The 23 decisions at the page's foot (`site/lib/decisions.ts`, `GENERATOR_DECISIONS`), each against this audit:

1. Merchant, every MWh at the hour's price: as stated; selling below zero is **finding 6**.
2. The fleet's shape, "nothing is trimmed": as stated; the hours are **right**; the month-start nameplate is **finding 7**.
3. The battery, "so its figure is an upper bound": **false**, **finding 5**.
4. The peaker, no start cost: **finding 9**.
5. The 90 and 95 percent months: as stated; checked on the default only.
6. The hub chosen prices everything: not tested.
7. The capture rate beside every capture price: **right** (the weightings, below).
8. One page, three questions: layout, not a model matter.
9. Costs from Lazard: as stated; the sources not read again.
10. Debt 60 percent at 8 percent over the life: arithmetic **right**; beside real revenue, **finding 2**.
11. Scenarios A and B: the shared block, checked on the battery page.
12. NPV at 12 percent: before tax, **finding 1**; on real flows, **finding 2**.
13. Solar 0.7 percent, a battery 2.6: the note's table is **finding 8**; a battery's cut one for one is the battery audit's finding 4.
14. A PPA's term is the life: as stated; what the contract is paid on is **finding 4**.
15. Values held at their bounds: not a model matter.
16. The downloads by license: not a model matter.
17. The plant with a battery beside it, "labelled an upper bound": not read.
18. The reader's own year: not a model matter.
19. The scenarios priced on the last twelve months: as stated.
20. The credits at 0, "the ITC arrives in year 1": the year is **finding 3**; tax is **finding 1**.
21. A plant at a node: not tested.
22. "A PPA is paid as generated by default": after year one the code pays it on year one's energy, not on what the plant generates: **finding 4**. The block is right not to degrade.
23. The grids: as stated.

## What was checked and found right

- **The revenue.** The public hourly file gives the page's 59.8523 per kW and 2,579.9 MWh per MW for its twelve months: price times the fleet's generation over the month's nameplate, summed.
- **The hours.** EIA-930's hour-ending time is read as the hour's start less one hour (`fuel_hours`, line 102). Checked against the sun: the output-weighted centre of the day falls at 12:43 in January (standard time) and 13:41 in June (daylight time), where solar noon is in Texas. An hour's shift would show.
- **The price.** The same hub-average real-time hourly mean as the battery page (complete hours only), from the same tables in the same order.
- **The two weightings the note owns up to** (section 6, items 7 and 8), recomputed from the public file: the model's capture price 23.20 against the capture file's 23.27 per MWh; the spans table's "price of every hour" (the mean of the months' means) 32.12 against 32.17 over the hours with a value. As stated, and small.
- **The debt.** 1,375 x 1,000 x 100 x 0.6 x `crf(0.08, 35)` = 7,078,769; coverage (59.85 - 12.5) / 70.79 = 0.67; the price for 1.25 times coverage, 39.14 per MWh; the breakeven PPA, 58.36 per MWh: each as the page.
- **The breakeven PPA price is a breakeven.** It is the contract price at which NPV to equity is zero, and the page keeps the coverage price under its own name. The battery page's finding 5 asks for this form.
- **The battery's dynamic program** (`battery_day`) finds the exact optimum of its own rules: each state of charge and energy cycled kept exactly, the better of two paths kept. Its rules, not its arithmetic, are finding 5.
- **The peaker's rule.** Run where the price is strictly above Henry Hub (the day's, or the last trading day's) times the heat rate plus variable O&M; CAISO adds the allowance cost. ERCOT's recomputed from the snapshot's own arrays: 48.15 per kW against the rows' 48.1461, the same 1,772 run hours. Its rule, not its arithmetic, is finding 9.

## Not covered, or left open

- **Wind, other grids and other hubs**: the same code, not recomputed. Of the other assets, ERCOT's battery (finding 5) and peaker (finding 9) were recomputed; their finance was not.
- **The plant with a battery beside it** (`seller_hybrid.py`) and the pasted profile: not read.
- **The capture file's own build** (`capture_price.py`, every hub and zone): not re-run; only the default hub's figure was recomputed (above).
- **The fleet's own curtailment.** EIA-930 counts what was generated, so the plant inherits the fleet's curtailment while it is paid the hub's price. Only an indication, outside the page's window: in the 1,271 hours `ercot_wind_solar_hsl_hourly` holds (28 September to 20 November 2026), the solar fleet's High Sustained Limit less its generation was 5.5 percent of its potential; only 11 percent of it fell in negative-price hours; valued at the hub-average price (USD 30.25 per MWh where curtailed) it was worth 6.7 percent of the generated energy. Much of that is local congestion, which a plant at its own node would see as a low price instead; the table's history is too short to measure the page's twelve months.
- **The capital cost's basis** (per kW of AC or DC capacity) against an output per MW of AC nameplate: not checked against Lazard's text.

## The deploys of this file (rule 8)

Every page is in review; this file changes no page. Snapshots as in the battery audit (`s9840-<label>-before` and `-after`, `node site/scripts/snapshot-live.mjs`).

- Push 1 (findings 1 to 5, with the battery file's record of its push 6), merge `df0ac9d0`; success about 21:42 UTC. `s9840-g1to5-before` against `s9840-g1to5-after`: 0 differences on 25 pages. Expected.
