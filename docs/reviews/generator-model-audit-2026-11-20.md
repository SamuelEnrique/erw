# What a generator earns: the model audited as a hostile expert would

Session 9841, 20 November 2026, the desktop's fifth window, after the battery page's audit (session 9840, `docs/reviews/battery-model-audit-2026-11-20.md`). Read as a developer's quantitative analyst who wants to find it wrong.

- The page: `/cost-of-power/seller`. The model: `warehouse/derived/merchant_revenue.py`. The page's arithmetic: `site/lib/merchant.ts`, `site/lib/seller2.ts`, `site/lib/seller/finance.ts`, `site/app/cost-of-power/seller/model.ts`.
- The note: `docs/methods/generator_earns_algorithm.md`. The decisions block: `site/lib/decisions.ts`, `GENERATOR_DECISIONS` (the note's section 13).
- Nothing changed on main but this file. No table written, no lock taken, no default moved.
- Each finding's test is on its own branch, `wip/audit-generator-<n>`, not requested for landing.

## How every number here was computed

- The default case: ERCOT, solar, 100 MW, priced at the hub average in real time; the page's last twelve months, October 2025 to September 2026: USD 59.85 per kW, coverage 0.67 on debt payments of USD 7,078,769.
- Revenue: the page's own public file, `site/public/seller/erw_2026_generator_hourly.csv` (72,384 hours: price, the fleet's solar MWh, the month's nameplate). It gives 59.8523 per kW and 2,579.9 MWh per MW for the page's twelve months.
- The battery comparisons: the battery page's public file (`site/public/battery/erw_2026_battery_dispatch.csv`), whose hourly energy price is the same ERCOT hub average in real time.
- Finance: `site/lib/seller/finance.ts` run by Node in each test, and a mirror. Default case: NPV at 12 percent USD -766.62 per kW (USD -76.66 million for 100 MW), the breakeven PPA price USD 58.36 per MWh (the note's), the price for 1.25 times coverage USD 39.14 (the note's).

## Findings, largest effect first

| # | Finding | Revenue, USD per kW (59.85) | NPV or price | Branch |
|---|---|---|---|---|
| 1 | The NPV holds no tax and no depreciation, yet is discounted at a cost of equity | none | NPV +240.52 per kW after federal tax | `wip/audit-generator-1` |
| 2 | Flat real flows, a fixed money debt payment and a money discount rate in one sum | none | NPV +59.72 to +77.42 per kW (inflation 2 to 2.5 percent) | `wip/audit-generator-2` |
| 3 | The same tax credit arrives in year 1 here and at year 0 on the battery page | none | a 30 percent credit on USD 1,110: 297.32 here, 333.00 there | `wip/audit-generator-3` |
| 4 | An as-generated PPA is paid on energy the plant no longer makes | none | breakeven PPA 58.36 against 61.50 per MWh | `wip/audit-generator-4` |
| 5 | The page's battery is "an upper bound", yet earns less than the battery page's program on the same prices | battery: -1.23 (-2.1 percent) at 4 hours | | `wip/audit-generator-5` |

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
