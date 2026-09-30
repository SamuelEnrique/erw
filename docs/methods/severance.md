# Severance tax: method

Built in session 40 for the severance tax engine v0 (`/severance`): Texas, Louisiana and New Mexico, for oil, gas and condensate where a state taxes condensate apart.

**Where the rules live.** The rules are a versioned site data file, `site/data/severance_rules.json` (version `2026-09-30.1`). They are not a warehouse table and are not in Supabase. The arithmetic is `site/lib/severance.ts`.

**Every rate cites a page.** Every rate, exemption, threshold and effective date cites a statute or state agency page whose text states it. Each was read as text on 2026-09-30, and the rule keeps the passage (`quote`) that states it. A check matched all 46 passages against the pages' text. A figure no page stated is not in the file; see "Left out" below.

**An estimate for education and planning, not tax advice.**

## Sources

| Id | Page |
|---|---|
| `tx_cpa_oil` | Texas Comptroller, Crude Oil Production Tax, https://comptroller.texas.gov/taxes/crude-oil/ |
| `tx_cpa_gas` | Texas Comptroller, Natural Gas Production Tax, https://comptroller.texas.gov/taxes/natural-gas/ |
| `tx_cpa_hist` | Texas Comptroller, History of Natural Gas and Crude Oil Tax Rates, https://comptroller.texas.gov/taxes/natural-gas/cong-rate-history.php |
| `tx_cpa_lp_gas` | Texas Comptroller, Tax Credit for Qualifying Low-Producing Gas Wells, https://comptroller.texas.gov/taxes/natural-gas/low-producing-wells.php |
| `tx_cpa_lp_oil` | Texas Comptroller, Tax Credit for Qualifying Low-Producing Oil Leases, https://comptroller.texas.gov/taxes/crude-oil/low-producing-leases.php |
| `tx_cpa_stacked` | Texas Comptroller, High-Cost Gas Exemption for Stacked Lateral Wells, https://comptroller.texas.gov/taxes/natural-gas/stacked-lateral-wells.php |
| `la_rs_47_633` | La. R.S. 47:633, Severance tax; rates; administration (as amended through Acts 2025, No. 373), https://legis.la.gov/Legis/Law.aspx?d=102399 |
| `la_rib_26_013` | Louisiana Department of Revenue, RIB No. 26-013 (June 2, 2026), the gas rate for July 1, 2026 to June 30, 2027 |
| `la_rib_26_014` | Louisiana Department of Revenue, RIB No. 26-014 (August 3, 2026), the horizontal well prices for FY 2027 |
| `nm_trd_taxes` | New Mexico Taxation and Revenue Department, Oil & Gas Production Taxes |
| `nm_trd_rates` | TRD, New Mexico Oil and Gas Production tax rates for 11/01/2021 through 08/31/2022 by county and suffix (spreadsheet) |
| `nm_trd_calc` | TRD, OGT Return Tax Due Calculation Method (Rev. 1, 2017-10-06) |

**The Texas Tax Code itself** (chapters 201 and 202) could not be read as text: the Legislature's statute site returns a script shell. The Comptroller's pages state every Texas figure used here.

## Texas

**Base rates, by market value:**

| Product | Rate | Since | Source |
|---|---|---|---|
| Oil | 4.6 percent | 1951-09-01 | `tx_cpa_oil`, `tx_cpa_hist` |
| Gas | 7.5 percent | 1969-10-01 | `tx_cpa_gas`, `tx_cpa_hist` |
| Condensate | 4.6 percent | 1953-08-27 | `tx_cpa_gas`, `tx_cpa_hist` |

**Fees, shown apart from the tax and the savings:**

- Oil Field Clean-Up Fee: $0.00625 per barrel, for report periods from September 2015.
- Oil-Field Cleanup Regulatory Fee on Natural Gas: $.000667 per Mcf.

**Oil:**

- **Enhanced Oil Recovery (Exempt Type 05):** 2.3 percent.
- **EOR using anthropogenic CO2 (Type 14):** "up to an additional 50 percent reduction in the tax rate". The calculator applies the reduction chosen to the 2.3 percent.
- **Two-Year Inactive Well:** 0.0 percent.
- **Low-producing lease credit (Type 11):**
  - It qualifies below 15 barrels per well per day over 90 days, or below 5 percent recoverable oil per barrel of produced water.
  - The credit is 25, 50 or 100 percent, set by the Comptroller-certified average oil price: over $30 none; over $25 to $30, 25 percent; over $22 to $25, 50 percent; $22 or less, 100 percent.
  - It combines with Types 05 and 14.

**Gas (one incentive per well per report period):**

- **High-cost gas (Type 5):**
  - 0.0 to 7.5 percent, set per well by drilling and completion costs against the prior fiscal year's median.
  - Capped by the statutory limit of 50 percent of drilling and completion costs in accumulated savings.
- **Low-producing well credit:**
  - It qualifies at 90 Mcf per day or less over the prior three months. Casinghead gas and condensate are not eligible.
  - The credit is 25, 50 or 100 percent by the certified average gas price: over $3.50 none; over $3 to $3.50, 25 percent; over $2.50 to $3, 50 percent; $2.50 or less, 100 percent.
- **0.0 percent rates:**
  - flared gas (Type 4);
  - gas that would otherwise be vented or flared, consumed within 1,000 feet;
  - restimulation wells (Type 17), until the exempted taxes reach the lesser of restimulation costs or $750,000;
  - two-year inactive wells (Type 16).

## Louisiana

**Base rates (`la_rs_47_633`):**

- **Oil:**
  - 12.5 percent of value for a well completed before July 1, 2025;
  - 6.5 percent for a well completed on or after that date;
  - the value is the higher of the first purchaser's gross receipts less trucking, barging and pipeline fees, or the posted field price.
- **Condensate:** 12.5 percent of gross value.
- **Gas:**
  - **15.14 cents per Mcf** for July 1, 2026 to June 30, 2027 (`la_rib_26_013`);
  - the 7-cent base times the gas base rate adjustment of 2.163, reset each July 1 (47:633(A)(5)(d)).

**Oil:**

- **Incapable well:** 6.25 percent. It qualifies at 25 barrels a day or less with at least 50 percent salt water, and every well on a multiple-well lease must be certified.
- **Stripper well:**
  - 3.125 percent at 10 barrels a day or less;
  - exempt in any month the average value is below $20 per barrel;
  - it stays certified until the well averages more than 10 barrels a day for a calendar month.
- **Inactive and orphan wells returned to production:**
  - production commencing before October 1, 2028: 3.125 and 1.565 percent;
  - on or after that date: 6.25 and 3.125 percent;
  - each for ten years, with certification applications from July 1, 2018 to June 30, 2028.
- **Horizontal wells:**
  - For FY 2027, 80 percent exempt, on an oil price of $73.28 (`la_rib_26_014`). The statutory tiers run from 100 percent at $70 or less to none above $110.
  - The exemption lasts 24 months or until payout.
- **Deep wells** (true vertical depth over 15,000 feet, production from August 1994): exempt for 24 months or until payout.
- **Orphan well enhancements** (production commencing October 1, 2021 to June 30, 2031): exempt, with the tax-equivalent amount remitted to the well's trust account from the fourth month.

**Gas:**

- **Low-pressure oil well** (50 psig or less): 3 cents per Mcf.
- **Incapable gas well** (under 250,000 cubic feet a day): 1.3 cents.
- **Inactive and orphan wells:** 3.785 and 1.8925 cents for FY 2027 (`la_rib_26_013`).
- **Horizontal wells:** 100 percent exempt for FY 2027 ($3.63 per MMBtu). The exemption runs 24 months or until payout for wells completed before July 1, 2025, and 18 months for wells completed on or after.
- **Deep wells:** exempt, as for oil.
- **Gas that is not taxed at all** (47:633(A)(5)(e)): gas injected for storage, gas vented or flared and not sold, lease and drilling fuel, gas used in producing natural resources in Louisiana, and gas used for carbon black. These volumes are listed, not computed: enter only taxable volume.

**Condensate:** the deep well exemption ("natural gas, gas condensate, and oil").

## New Mexico

**Four production taxes, named as TRD names them:**

- the Oil and Gas Severance Tax;
- the Oil and Gas Conservation Tax;
- the Oil and Gas Emergency School Tax;
- the Oil and Gas Ad Valorem Production Tax.

**The base.** All four are levied on taxable value: the price at the production unit, less royalties paid the United States, New Mexico or a tribe or pueblo, and less reasonable trucking to the first place of market (`nm_trd_taxes`). The calculator subtracts the royalty share and trucking the user enters.

**The rates** come from TRD's latest published table found, effective November 1, 2021 through August 31, 2022 (`nm_trd_rates`):

| Tax | Oil | Gas |
|---|---|---|
| Severance | 3.75 percent | 3.75 percent |
| Emergency school | 3.15 percent | 4 percent |
| Conservation | 0.19 percent to 2021-09-30, 0.24 percent from 2021-10-01 | 0.19 percent |

- **Conservation on oil** is a choice on the page. The table shows both rates, and the rule that moves it was not read.
- **Ad valorem production** varies by county and district. The user enters the unit's rate.
- **The TRD calculation note** (`nm_trd_calc`) shows the same oil rates in a 2017 example, and says each tax is rounded to the cent separately. The calculator does not round per tax.
- **The Oil and Gas Production Equipment Ad Valorem Tax** is annual (due November 30) and is not computed.

## The calculator

- **Tax at the base rate:** the taxable value times each base rate, or the volume times a per-unit rate.
- **Tax with the exemptions chosen:**
  - One rate-group option (a reduced rate, a per-unit rate, an exemption share, or a credit) replaces the first base component.
  - A credit-group option (Texas's low-producing oil lease credit) then reduces the total.
- **Savings** is the difference. Fees are shown apart.
- **Default prices:** the mean of the latest complete calendar month of the warehouse's EIA daily spot prices (`eia_fuel_spot_prices`), labelled as an assumption and editable.
  - Oil and condensate use WTI Cushing.
  - Gas uses Henry Hub, quoted per MMBtu and applied per Mcf as if one Mcf held one MMBtu.
  - A hub price is not the value at the well.
- **Tests:** `site/scripts/test-severance.mjs` checks 19 hand-computed cases, run by `tests/test_session40.py`.

## Left out: no page read states them

**Texas:**

- how long EOR (Type 05 and 14) lasts;
- the Railroad Commission's certification terms;
- the Comptroller's marketing-cost policy for gas (the page "Audit Policy on Natural Gas Marketing Costs" was not read), so no deduction is computed;
- the statute text of Tax Code chapters 201 and 202.

**Louisiana:**

- the oilfield site restoration fee (R.S. 30:87, amended by Act 662 of 2026), which is a fee, not severance tax;
- the posted field price comparison;
- the natural gas liquids rules beyond the gas rate.

**New Mexico:**

- the rates in force in 2026: no TRD table after August 2022 was found;
- the rule that sets the conservation tax at 0.19 or 0.24 percent;
- any price-based change in the emergency school or severance tax;
- New Mexico's reduced rates for stripper wells, enhanced recovery or well workovers (the NMSA text, on NMOneSource, could not be read as text);
- products H and C of TRD's table, which the table does not name;
- the equipment ad valorem tax.
