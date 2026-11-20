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

## 1. The NPV holds no tax and no depreciation

- **Where.** `site/lib/seller/finance.ts` lines 241 to 247 (`flows`: no tax term), line 128 (`defaultsOf`: `itc: 0`, `ptc: 0`). The note, section 11.3 line 522 ("No tax, no tax credit, ..."), section 11.6 line 547. Decisions: "The NPV is discounted at 12 percent, Lazard's cost of equity" (`site/lib/decisions.ts` line 82) and the credits at 0 (line 98).
- **Why it is wrong.** A cost of equity is a return after tax; the flows it discounts are before tax, with no depreciation. The battery page's finding 8, on a plant whose capital is 1,375 per kW and 60 percent debt, so the interest and the depreciation weigh more.
- **How much.** The default case after federal tax (21 percent; 5-year MACRS, half-year convention; interest deductible on the level loan's schedule; losses used as they arise), every other figure the page's: NPV USD -526.10 per kW against -766.62, +240.52 (USD 24.1 million for 100 MW). Revenue and coverage do not move.
- **The credits.** The page's credit fields (investment and production) default to 0. Whether a new solar plant still qualifies (the credits' end dates and start-of-construction rules) is the project's; this audit does not claim it does.
- **The test.** `tests/test_audit_generator_1.py` on `wip/audit-generator-1`: through `finance.ts` the default holds no credit, the debt payment is 7,078,769 for 100 MW and NPV -766.62; after tax, -526.10.
- **Not fixed.** The owner's ruling, with the battery page's finding 8.
