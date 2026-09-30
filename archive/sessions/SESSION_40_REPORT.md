# Session 40 report: severance tax engine v0 (Texas, Louisiana, New Mexico)

Energy Research Warehouse (ERW), session 40, run 2026-09-30 from 18:23 to about 18:45 UTC. **Wall time about 22 minutes,** against a 45-minute target.

**API spend: USD 0.00, confirmed.** No model call. The cost ledger's last row is 05:12 UTC.

- **No data pull and no Supabase table.** The rules are a versioned site data file. Statute and agency pages were read as text.
- **Nothing released or deleted.** No force push.
- **Deployed and checked live:** routes 50 of 50, values 1,631 of 1,631.

**The daily job:**

- **The scheduled run** of 2026-09-30 started at 18:40 UTC and was still running when this report was written. Nothing had landed on origin/main to merge.
- **A manual run** (workflow_dispatch, 18:24 UTC) failed after about 70 seconds. It was not started by this session.

## What was built

- **`site/data/severance_rules.json` (version `2026-09-30.1`):** every rule carries its source and the passage that states it. A check matched all 46 passages against the pages' text.
- **`site/lib/severance.ts`:** the arithmetic.
- **`/severance`,** in a new **Tools** menu:
  - inputs: state, product, monthly volume (bbl or Mcf), and price;
  - state-specific inputs: Louisiana completion date and transport; New Mexico royalties, trucking, conservation rate and ad valorem rate;
  - one reduced rate or exemption, and Texas's oil lease credit;
  - output: tax at the base rate, tax with the exemptions, and the savings, each line citing its rule. The chosen exemption's who, what and how long are shown with its quote.
- **A full rule list on the page,** each rule linked to its source.
- **Default prices** are the warehouse's EIA spot means for August 2026, the latest complete month, labelled as assumptions and editable:
  - WTI $83.90, from 21 days (row mean 83.8976);
  - Henry Hub $2.79 (2.7852), applied per Mcf as if one Mcf held one MMBtu, and the page says so.
- **The disclaimer:** "An estimate for education and planning, not tax advice". Deductions are listed, and computed only where the rule states them.
- **Method:** `docs/methods/severance.md`.

## Every rule with its citation

Quotes are verbatim from the pages, apart from dashes and quote marks normalized. The full passages are in the JSON.

### Texas (Texas Comptroller)

| Rule | Figure | Citation |
|---|---|---|
| Oil production tax | 4.6% of market value; since 1951-09-01 | comptroller.texas.gov/taxes/crude-oil/ ("Oil production tax: 4.6 percent (.046) of market value of oil"); rate history page ("09-01-1951 to date 4.6% of value") |
| Gas production tax | 7.5% of market value; since 1969-10-01 | comptroller.texas.gov/taxes/natural-gas/; rate history ("10-01-1969 to date 7.5% of value") |
| Condensate | 4.6% of market value; since 1953-08-27 | natural gas page; rate history ("08-27-1953 to date 4.6% of value") |
| Oil Field Clean-Up Fee | $0.00625/bbl, report periods from September 2015 | crude oil page |
| Oil-Field Cleanup Regulatory Fee on gas | $.000667 per Mcf | natural gas page |
| EOR (Type 05) | 2.3% | crude oil page |
| EOR with anthropogenic CO2 (Type 14) | up to an additional 50% reduction in the rate; four conditions on the CO2 | crude oil page |
| Two-year inactive well, oil | 0.0% | crude oil page |
| Low-producing oil lease credit (Type 11) | <15 bbl/well/day over 90 days, or <5% recoverable oil per bbl of water; credit 0/25/50/100% at certified price >$30 / $25-30 / $22-25 / <=$22; combines with 05 and 14 | comptroller.texas.gov/taxes/crude-oil/low-producing-leases.php; crude oil page (multiple exempt types) |
| High-cost gas (Type 5) | 0.0-7.5% per well, by costs against the prior fiscal year's median; cap: savings of 50% of drilling and completion costs | natural gas page; stacked lateral wells page |
| Low-producing gas well credit | <=90 Mcf/day over the prior three months; credit 0/25/50/100% at certified price >$3.50 / $3-3.50 / $2.50-3 / <=$2.50; not with high-cost gas in the same period; casinghead gas and condensate ineligible | low-producing-wells.php; natural gas page |
| Flared gas (Type 4); gas otherwise vented or flared (within 1,000 feet); restimulation (Type 17, to the lesser of costs or $750,000); two-year inactive (Type 16) | 0.0% each | natural gas page |

### Louisiana (La. R.S. 47:633; LDR)

| Rule | Figure | Citation |
|---|---|---|
| Oil | 12.5% of value for wells completed before July 1, 2025; 6.5% on or after; value = higher of gross receipts less trucking, barging and pipeline fees, or the posted field price | R.S. 47:633(A)(3)(a) |
| Condensate | 12.5% of gross value | 47:633(A)(4) |
| Gas | 15.14 cents per Mcf, July 1, 2026 to June 30, 2027 (7 cents x adjustment 2.163) | LDR RIB 26-013; 47:633(A)(5)(d) (annual July reset) |
| Incapable oil well | 6.25% (25 bbl/day or less, 50% salt water; all wells on the lease certified) | 47:633(A)(3)(b) |
| Stripper well | 3.125% (10 bbl/day or less); exempt when the average value is under $20/bbl | 47:633(A)(3)(c)(i) |
| Inactive and orphan wells | oil 3.125% and 1.565% (commencing before Oct 1, 2028; 6.25% and 3.125% after); gas 25% and 12.5% of the rate, 3.785 and 1.8925 cents for FY27; ten years; applications to June 30, 2028 | 47:633(A)(3)(c)(iii); RIB 26-013 |
| Horizontal wells | FY27: oil 80% exempt ($73.28), gas 100% ($3.63); oil 24 months or payout; gas 24 months or payout before July 1, 2025 completion, 18 months after | RIB 26-014; 47:633(A)(3)(d) |
| Deep wells (>15,000 ft TVD, production after July 31, 1994) | exempt 24 months or payout, oil, gas and gas condensate | 47:633(A)(5)(d)(v) |
| Orphan well enhancements (production Oct 1, 2021 to June 30, 2031) | exempt; tax-equivalent amount remitted to the trust account from month four | 47:633(A)(3)(c)(iii)(ff) |
| Low-pressure oil-well gas (50 psig or less) | 3 cents per Mcf | 47:633(A)(5)(b); RIB 26-013 |
| Incapable gas well (<250,000 cf/day) | 1.3 cents per Mcf | 47:633(A)(5)(c); RIB 26-013 |
| Gas not taxed (storage injection, vented or flared unsold, lease and drilling fuel, gas used in production, carbon black) | listed, not computed | 47:633(A)(5)(e) |

### New Mexico (TRD)

| Rule | Figure | Citation |
|---|---|---|
| The four production taxes and the taxable value (price less royalties to the US, NM or a tribe, less trucking) | named as TRD names them | TRD, Oil & Gas Production Taxes |
| Oil and Gas Severance Tax | 3.75% (oil and gas) | TRD rate table, 2021-11-01 to 2022-08-31; TRD calculation note (2017 example) |
| Oil and Gas Emergency School Tax | oil 3.15%, gas 4% | TRD rate table |
| Oil and Gas Conservation Tax | 0.19%; oil 0.24% from 2021-10-01 in the table (a choice on the page) | TRD rate table |
| Oil and Gas Ad Valorem Production Tax | by county and district: the user enters the rate | TRD, Oil & Gas Production Taxes |
| Production Equipment Ad Valorem Tax | annual, due November 30: listed, not computed | TRD, Oil & Gas Production Taxes |

## Figures left out for lack of a source

- **Texas:**
  - the Tax Code chapters 201 and 202 themselves: the statute site returned only a script shell;
  - how long EOR (Types 05 and 14) lasts;
  - the Railroad Commission's certification criteria;
  - the marketing-cost deduction for gas (the Comptroller's audit policy page was not read);
  - the latest Comptroller-certified average prices. The low-producing gas page lists report periods to December 2026 at $1.18 to $1.42 per Mcf, which looked inconsistent with the date, so the user picks the credit tier.
- **Louisiana:**
  - the oilfield site restoration fee (R.S. 30:87, amended by Act 662 of 2026, effective July 1, 2026), which is a fee, not the severance tax;
  - the posted field price test;
  - the natural gas liquids equivalent volumes.
- **New Mexico:**
  - **the rates in force in 2026:** the latest TRD rate table found ends August 31, 2022. The page states this;
  - the rule that sets conservation at 0.19 or 0.24 percent;
  - any price-based step in the emergency school or severance tax;
  - reduced rates for stripper wells, enhanced recovery and workovers: NMSA 7-29-4 and the others, on NMOneSource, did not render as text;
  - what TRD's product kinds H and C are;
  - per-tax rounding to the cent, as TRD's note does.

## Test cases

`site/scripts/test-severance.mjs`, run by `tests/test_session40.py`, checks 19 hand-computed cases. All pass:

| # | Case | Hand result |
|---|---|---|
| 1 | TX oil, 1,000 bbl at $70 | base $3,220.00, fee $6.25 |
| 2 | TX oil with EOR | $1,610.00 |
| 3 | TX oil with CO2 EOR (50%) and a 50% lease credit | $402.50 |
| 4 | TX gas, 10,000 Mcf at $3 | $2,250.00, fee $6.67 |
| 5 | TX gas, high-cost gas at 2.5% | $750.00 |
| 6 | TX gas, low-producing credit 100% | $0.00 |
| 7 | TX condensate, 500 bbl at $60 | $1,380.00 |
| 8 | LA oil, pre-2025, $2 transport | $8,500.00 |
| 9 | LA oil, post-2025 | $4,420.00 |
| 10 | LA stripper | $2,125.00 |
| 11 | LA stripper at $19 | exempt, $0.00 (base $2,375.00) |
| 12 | LA horizontal, FY27 | $1,700.00 |
| 13 | LA orphan | $1,064.20 |
| 14 | LA gas, 10,000 Mcf | $1,514.00 |
| 15 | LA incapable gas well | $130.00 |
| 16 | LA inactive gas well | $378.50 |
| 17 | LA condensate, deep well | base $3,750.00, with $0.00 |
| 18 | NM oil at $70 with 12.5% royalty and $1 trucking (taxable $60,250), conservation 0.24%, ad valorem 1.0% | $4,904.35 |
| 19 | NM gas at $3 | $2,382.00 |

The script also checks that every option computes, never raises the tax, and cites a source the file names. A second test checks that every rule has a citation, a quote and an https URL.

**`tests/`:** 78 of 78.

## Decisions made without a human

1. **Texas figures come from the Comptroller's pages,** which the prompt lists as a source. The Tax Code text could not be read.
2. **New Mexico's rates** come from TRD's latest table found (2021-22), labelled with its dates rather than left out. New Mexico's taxes are the heart of a New Mexico calculator, and the page says plainly that 2026 rates were not found.
3. **One rate-group option per well and month.** Texas says a gas well cannot report both low-producing and high-cost gas in one period. The Texas oil lease credit stacks, as the Comptroller's page allows.
4. **The Texas credit tier is picked by the user.** The tier follows the Comptroller-certified price, not the price entered.
5. **The CO2 EOR reduction** is applied to the 2.3 percent EOR rate.
6. **Henry Hub per MMBtu is used per Mcf** as a labelled, editable assumption.
7. **Deductions are computed only where the rule states them:** Louisiana's transport on oil and condensate, New Mexico's royalties and trucking.
8. **The nav gets a new "Tools" group.**

## Open questions for Samuel (only you can answer these)

1. **Texas market value:** in your Ryan work, which marketing costs did the Comptroller allow against gas market value, and how were they documented? Should the calculator take a marketing-cost input for Texas gas?
2. **High-cost gas:** how did clients estimate their Type 5 rate before certification? Is the Comptroller's estimator the practical starting point, and how often did the 50 percent cap bind?
3. **Low-producing credits:** do operators plan on the certified price tiers, or treat the credit as a windfall? Should the calculator fetch or store the Comptroller's monthly certified prices?
4. **Louisiana value:** how often does the posted field price exceed gross receipts less transport in practice, and which transport charges did LDR accept?
5. **Louisiana horizontal payout:** how is payout tracked in practice (the well cost statement by an independent CPA), and which well costs were disputed most?
6. **New Mexico current rates:** where do practitioners get the current rate table by suffix? The table TRD links ends August 2022. And what triggers the 0.24 percent conservation rate?
7. **New Mexico incentives:** which reduced rates (stripper, enhanced recovery, workovers) do clients claim, and are they in force now?
8. **Refund work:** which exemptions were most often missed or under-claimed, and so worth a "you may qualify" prompt on the page?
9. **Scope:** which states next (Oklahoma, North Dakota, Colorado, Wyoming, Pennsylvania's impact fee)? And should the tool model a lease with several wells?

## Skipped

- A price-series check key for the default prices: they are a month's mean, recomputed and checked by hand (83.8976 and 2.7852 from 21 days each).
- Per-tax cent rounding for New Mexico.
