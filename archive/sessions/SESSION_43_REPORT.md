# Session 43 report: electricity bill explainer v0 (education)

Energy Research Warehouse (ERW), session 43, run 2026-09-30 from 19:35 to about 19:58 UTC. **Wall time about 23 minutes,** against a 50-minute target.

**API spend: USD 0.00, confirmed.** No model call. The cost ledger's last row is 05:12 UTC.

- **No data pull, no upload, no user data, no Supabase table.** Tariff pages were read as text.
- **Deployed and checked live:** routes 51 of 51, values 1,637 of 1,637 (6 on `/learn/bill`).
- **Nothing to merge:** the daily job did not land. Run 12 was still in progress at 19:55 UTC.

## What was built

- **`site/data/bill_rules.json` (version `2026-09-30.1`):** each line gives what it is, why it exists (one plain sentence), its rate and basis, and its source with the quoted passage and effective date. A check matched all 36 passages against the tariff text, whitespace ignored.
- **`site/lib/bill.ts`:** the arithmetic.
- **`/learn/bill`,** in a new **Learn** menu that also lists the seven grid pages and the events:
  - choose California or Texas; enter monthly kWh (600 by default, labelled an assumption);
  - California also takes the peak share (20 percent by default, the tariff's own example), season, baseline territory, income tier and the climate credit;
  - Texas takes the retailer's energy charge;
  - each bill is drawn line by line, and each line opens to its what, why, rate detail and quoted passage;
  - totals and per-kWh all-in;
  - a bar splitting the total into wholesale energy and the rest, with a sentence naming what the rest pays for;
  - "written, cited" chips on the text;
  - the default bills computed on the server and checked;
  - a ten-term glossary, each term naming its source;
  - links to `/grid/caiso`, `/grid/ercot` and `/cost-of-power`.

## Every line and rate, with its source

### California: PG&E Electric Schedule E-TOU-C

Source: https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_SCHEDS_E-TOU-C.pdf. Baseline territory: Electric Preliminary Statement Part A.

| Line | Rate | Effective | Passage (short) |
|---|---|---|---|
| Total energy rate, summer peak / off-peak | $0.52240 / $0.39940 per kWh | 2026-06-01 (Sheet 2) | "Summer Total Usage $0.52240 (R) $0.39940 (R)" |
| Total energy rate, winter peak / off-peak | $0.39757 / $0.36757 | 2026-06-01 (Sheet 2) | "Winter Total Usage $0.39757 (R) $0.36757 (R)" |
| Baseline credit | ($0.08140) per baseline kWh | 2026-06-01 (Sheet 2) | "Baseline Credit (Applied to Baseline Usage Only) ($0.08140)" |
| Base Services Charge, Income Tier 1 / 2 / 3 | $0.19713 / $0.39688 / $0.79343 per day | 2026-06-01 (Sheet 2) | "Income Tier 3 $0.79343 (N)" |
| Base services components, Tier 3 | Distribution $0.36945, Public Purpose Program $0.31065, Nuclear Decommissioning $0.00000, New System Generation Charge $0.11333 | 2026-03-01 (Sheet 4) | quoted |
| California Climate Credit | ($36.18) per household | 2026-06-01 (Sheet 2) | "(per household, semi-annual payment occurring in the August and September bill cycles) ($36.18)" |
| Generation, summer / winter, peak and off-peak | $0.20782, $0.10482 / $0.13710, $0.11042 | 2026-03-01 (Sheet 3) | quoted |
| Bundled PCIA | ($0.01011) | Sheet 3 | quoted |
| Distribution, summer / winter | $0.20388, $0.18388 / $0.14977, $0.14645 | Sheet 3 | quoted |
| New System Generation Charge | $0.00000 | Sheet 3 | quoted |
| Conservation Incentive Adjustment | baseline ($0.02786), over baseline $0.05354 | Sheet 3 | quoted |
| Transmission | $0.04638 | Sheet 3 | quoted |
| Transmission Rate Adjustments | $0.00453 | Sheet 3 | quoted |
| Reliability Services | $0.00013 | Sheet 3 | quoted |
| Public Purpose Programs | $0.00614 | Sheet 3 | quoted |
| Nuclear Decommissioning | ($0.00002) | Sheet 3 | quoted |
| Competition Transition Charges | $0.00027 | Sheet 3 | quoted |
| Energy Cost Recovery Amount | $0.00002 | Sheet 3 | quoted |
| Wildfire Fund Charge | $0.00591 | Sheet 3 | quoted |
| Wildfire Hardening Charge | $0.00391 | Sheet 3 | quoted |
| Recovery Bond Charge / Credit | $0.00857 / ($0.00857) | Sheet 3 | quoted |

**Supporting rules:**

- **Peak hours:** 4 to 9 p.m. every day (Sheet 5).
- **Peak share pro-rated across the baseline** (Sheet 1: "if twenty percent of a customer's usage is in the peak period, then twenty percent of the total usage in each tier will be treated as on-peak usage").
- **Baseline quantities, Code B, by territory** (Sheet 5). Territory T is 6.5 kWh a day in summer and 7.5 in winter.
- **San Francisco is territory T** (Preliminary Statement Part A: "SAN FRANCISCO All T").

**A cross-check the tariff allows.** The Sheet 3 components, effective March 1, add up exactly to the Sheet 2 totals, effective June 1. Summer peak: 0.46886 plus the 0.05354 over-baseline adjustment is 0.52240. The baseline credit equals the over-baseline adjustment less the baseline one (0.05354 + 0.02786 = 0.08140). The page draws the unbundled lines, and the test checks them against the totals.

### Texas: Oncor Tariff for Retail Delivery Service

Source: https://www.oncor.com/content/dam/oncorwww/documents/about-us/regulatory/tariff-and-rate-schedules/Tariff%20for%20Retail%20Delivery%20Service.pdf

| Line | Rate | Effective | Where |
|---|---|---|---|
| Customer Charge | $1.48 per month | 2026-06-01 | 6.1.1.1.1 Residential Service, Sheet 1.1 |
| Metering Charge | $2.58 per month | 2026-06-01 | Sheet 1.1 |
| Distribution System Charge | $0.036043 per kWh | 2026-06-01 | Sheet 1.1 |
| Transmission Cost Recovery Factor (TCRF) | $0.019046 per kWh | 2026-08-01 | Rider TCRF, 6.1.1.6.1 |
| Energy Efficiency Cost Recovery Factor (EECRF) | $0.001487 | 2026-03-01 | Rider EECRF, 6.1.1.6.3 |
| Distribution Cost Recovery Factor (DCRF) | $0.000000 | 2026-06-01 | Rider DCRF, 6.1.1.6.4 |
| Nuclear Decommissioning Charge (NDC) | $0.000000 | | Rider NDC, 6.1.1.5.1 |
| Rate Case Expense Surcharge (RCE) | $0.000086 | Docket No. 58306, until $8,291,399 is billed | Rider RCE, 6.1.1.6.5 |
| Mobile Generation (MG) | $0.001027 | 2025-12-01 | Rider MG, 6.1.1.6.6 |
| Interim Surcharge (IS) | $0.003633 | through December 2026 | Rider IS, 6.1.1.6.7 |
| Retail energy charge | **input**; default **$0.0907/kWh** | | see below |

**The default energy charge is labelled as an assumption.** The derivation: EIA's July 2026 Texas residential average, 158.8 USD/MWh (warehouse table `eia_retail_electricity_prices`, entity `eia:retail_price:TX:RES`), less Oncor's per-kWh charges ($0.061322), less its fixed charges spread over 600 kWh ($4.06 / 600). That gives 0.090711, rounded to 0.0907, so the default bill at 600 kWh matches the state average. The page tells readers to enter the energy charge from their plan's Electricity Facts Label.

## Figures left out for lack of a source

- **California:**
  - Direct Access and Community Choice Aggregation bills (the tariff's Special Condition 8);
  - taxes and city fees (utility users' taxes, franchise fees);
  - the all-electric (Code H) baseline, which is in the file but not offered on the page;
  - the medical baseline exemption from the Wildfire Fund Charge (noted in the tariff).
- **Texas:**
  - taxes and fees a retailer adds (sales tax where it applies, the PUC assessment, gross receipts reimbursement): not in Oncor's tariff;
  - any ERCOT fee billed by the retailer;
  - a real retail plan price (the default is derived, as above).
- **Wholesale reference:** CAISO's main hub in the warehouse is SP15, while PG&E homes are mostly in the NP15 zone. CAISO has no complete month held, so the latest month (2026-09, partial) is used and labelled.

## Test cases

`site/scripts/test-bill.mjs`, run by `tests/test_session43.py`. All pass; `tests/`: 80 OK.

| Case | Hand result |
|---|---|
| CA summer, 600 kWh (T, 20% peak, Tier 3, 30 days): 120 x 0.52240 + 480 x 0.39940 = 254.40; baseline credit 195 x 0.08140 = 15.873; base services 30 x 0.79343 = 23.8029 | **$262.3299** |
| CA summer, 1,000 kWh: 424.00 - 15.873 + 23.8029 | **$431.9299** |
| CA winter, 600 kWh (baseline 225 kWh): 224.142 - 18.315 + 23.8029 | $229.6299 |
| TX, 600 kWh: 600 x 0.0907 + 600 x 0.061322 + 4.06 | **$95.2732** |
| TX, 1,000 kWh: 90.70 + 61.322 + 4.06 | **$156.082** |

Also checked:

- California's unbundled lines equal the tariff's total rates in each case.
- Every line has a quote, a date and an https source.
- Texas's default is derived as labelled.

**check-values** recomputes each default total its own way: California by the total rates of Sheet 2, not the unbundled lines. It also recomputes the wholesale dollars and share from `cost_of_power_monthly`.

## The wholesale share on each default bill (600 kWh)

| Bill | Total | Wholesale energy | Share | Price used |
|---|---|---|---|---|
| California (PG&E, summer) | $262.33 | $23.24 | **8.86%** | CAISO SP15 load-weighted real-time, 38.73 USD/MWh, 2026-09 (partial month) |
| Texas (Oncor) | $95.27 | $22.02 | **23.11%** | ERCOT hub average load-weighted real-time, 36.70 USD/MWh, 2026-08 |

## A site fix

The first local build lost the NYISO and SPP grid pages' queue reads to Supabase statement timeouts, even with session 39's one retry. Daily run 12 was running at the time, and the same query took 0.2 seconds a minute later. The site's Supabase reader now retries a statement timeout twice (after 1 and 3 seconds). The rebuilt pages held every queue value, and the live check is whole.

## Decisions made without a human

1. **California's defaults:** bundled service, Income Tier 3, Code B baseline, territory T (San Francisco), summer (the season on 2026-09-30), 20 percent peak (the tariff's own example), 30 days, no climate credit.
2. **Texas's default energy charge** is derived from EIA's state average, labelled, and editable.
3. **The page shows PG&E's unbundled components, not only the totals,** because they explain the bill line by line and add up to the totals exactly.
4. **The nav's Learn group:** the bill page, plus the grid pages and events as links.
5. **The retry change** above.

## Open questions

1. **Taxes and city fees** differ by city in both states. Add a line per city from a cited source, or keep them out and say so, as now?
2. **More bills:** another California utility (SCE, SDG&E), or a Texas retailer's real Electricity Facts Label as the default?
3. **A zone-level wholesale reference for PG&E (NP15):** the warehouse's CAISO prices hold SP15 as the main hub.
4. **Daily run 12** was still in progress at 19:55 UTC. Session 42 waits on it.
