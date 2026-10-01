# Severance tax: method

Built in session 40 for the severance tax engine v0 (`/severance`): Texas, Louisiana and New Mexico, for oil, gas and condensate where a state taxes condensate apart.

**Where the rules live.** The rules are a versioned site data file, `site/data/severance_rules.json` (version `2026-09-30.2`; session 41 added the Texas Tax Code sections, the Comptroller's certified prices and New Mexico's 2026 rates). They are not a warehouse table and are not in Supabase. The arithmetic is `site/lib/severance.ts`.

**Every rate cites a page.** Every rate, exemption, threshold and effective date cites a statute or state agency page whose text states it. Each was read as text on 2026-09-30, and the rule keeps the passage (`quote`) that states it. A check matched all 72 passages (46 in session 40, 26 more in session 41) against the pages' text. A figure no page stated is not in the file; see "Left out" below.

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
| `tx_code_201`, `tx_code_202` | Texas Tax Code chapters 201 (gas) and 202 (oil), https://statutes.capitol.texas.gov/Docs/TX/htm/TX.201.htm and TX.202.htm (session 41). The site's pages are a script viewer; the text is the file it loads, https://tcss.legis.texas.gov/resources/TX/htm/TX.201.htm and TX.202.htm |
| `nm_trd_rates_2026` | TRD, New Mexico Oil and Gas Production tax rates for 04/01/2026 through 08/31/2026 by county and suffix (spreadsheet, revised; session 41) |

**The Texas Tax Code itself** (chapters 201 and 202) could not be read in session 40, because the statute site is a script viewer. Session 41 read the files it loads. Each Texas rule now cites its section beside the Comptroller's page (`code` in the JSON).

## Texas

**What the code adds (session 41):**

| Rule | Section | What the code states |
|---|---|---|
| Oil | Sec. 202.052(a) | 4.6 percent of market value or 4.6 cents a barrel, whichever is greater. The calculator applies the greater. |
| Gas | Sec. 201.052(a) | 7.5 percent of market value |
| Condensate | Sec. 201.055(b) | the oil rate of Sec. 202.052. The calculator applies 4.6 percent and not the per-barrel alternative, which the Comptroller's page does not state for condensate. |
| EOR | Secs. 202.052(b), 202.054(g) | 2.3 percent, for 10 years from the month after the Railroad Commission certifies a positive production response |
| EOR with anthropogenic CO2 | Sec. 202.0545(a), (b) | an additional 50 percent reduction until the 30th anniversary of the Comptroller's first approval, prorated to the anthropogenic share of the CO2 |
| Two-year inactive wells | Sec. 202.056(b); gas by Sec. 201.053(4) | a five-year exemption |
| High-cost gas | Sec. 201.057(c) | 7.5 percent less 7.5 percent times the well's drilling and completion costs over twice the prior fiscal year's median, never below zero, for 120 consecutive months or until the reduction equals 50 percent of those costs. The calculator takes the cost ratio. |
| Restimulation | Sec. 202.062(c) | exempt until the earlier of 36 consecutive months or the lesser of restimulation costs or $750,000 in exempted tax |
| Flared gas from oil wells | Sec. 201.053(2) | not taxed |
| Gas otherwise vented or flared, consumed within 1,000 feet | Sec. 201.061(b) | not taxed |
| Low-producing credits | Secs. 201.059(b), 202.058(c) | the Comptroller certifies each month the average taxable price over the previous three months, **adjusted to 2005 dollars** |

**Why the certified prices look low.** They are in 2005 dollars: gas at $1.17 to $1.97 per Mcf through 2025 and 2026. That is what session 40 found odd.

**The "date inconsistency."** Session 40 saw rows for September to December 2026 on the Comptroller's pages. In the page source those four rows sit inside an HTML comment (`<!-- ... -->`), so a browser never shows them. They are placeholders, copied row for row from September to December 2025.

**The certified prices in the rules file.** The file keeps the published rows only, January 2025 to August 2026, for gas and oil. The latest, August 2026, is gas $1.36 per Mcf (100 percent credit) and oil $53.55 per barrel (no credit). The calculator picks the credit tier from the certified price of the report period the reader chooses.

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

**The rates** come from TRD's latest published table, effective April 1, 2026 through August 31, 2026 (`nm_trd_rates_2026`, session 41). Session 40's link filter missed it and used the 2021-22 table. TRD had not published a table from September 2026 when it was read on 2026-09-30.

| Tax | Oil | Gas |
|---|---|---|
| Severance | 3.75 percent | 3.75 percent |
| Emergency school | 3.15 percent | 4 percent |
| Conservation | 0.24 percent (from 2026-04-01) | 0.19 percent (2025-09-01 to 2026-08-31) |
| Ad valorem production | the district's rate, 0.7105 to 1.7249 percent (35 county, district and suffix rows) | the same |

- **Why AD /2 is the production rate.** The table's "AD /2" column is the ad valorem production rate: SEV + SCHOOL + CONS + AD /2 equals its Total Rate on every oil and gas row. Its "AD VAL", twice that, is the equipment tax.
- **The reader picks the district** from the table's list.
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
- **Tests:** `site/scripts/test-severance.mjs` checks 26 hand-computed cases, run by `tests/test_session40.py`: 19 from session 40 and 7 from session 41 (the per-barrel floor, high-cost gas by cost ratio, the certified tiers and New Mexico's 2026 rates). Session 41 replaced one case, since high-cost gas now takes a cost ratio.

## The lease tool (session 45, v0.2)

`/severance/lease` takes a lease file: one row per well and month, with `state`, `well_id`, `month` and the month's oil (bbl), gas (Mcf) and condensate (bbl), and optional prices and well facts (the template lists each column and the rule that uses it). The file is read with the browser's File API and computed in the page (`site/lib/lease.ts` on `site/lib/severance.ts`); it is never sent to the server, and the results download is made in the page. A sample of clearly fictional wells shows each flag.

**Prices.** A blank price is the month's mean of the warehouse's EIA daily spot prices (`eia_fuel_spot_prices`): WTI Cushing for oil and condensate, Henry Hub for gas (USD per MMBtu, applied per Mcf as if one Mcf held one MMBtu), each labeled with the number of days averaged. A hub price is not the value at the well. A month the warehouse does not hold is not computed until a price is entered.

**Per well, month and product:** the base tax (Louisiana's oil rate from the completion date: 6.5 percent on or after July 1, 2025, else 12.5 percent, and 12.5 percent when no date is given; New Mexico's ad valorem rate from the district), the tax with the rules the reader ticks (one reduced rate per well and product, and the Texas low-producing oil credit beside it, as the calculator allows), and the regulatory fees apart.

**"May qualify" flags.** A flag means the well's own numbers meet the rule's thresholds. The state still certifies or designates the well; the flag says so. Each flag cites its rule and states the numbers:

| Rule | The test on the file's numbers |
|---|---|
| TX low-producing oil lease (`tx_lp_oil`) | The lease's oil wells (Texas wells with oil that month) average less than 15 bbl per well per day over the months of the 90 days ending with the month that the file holds, or less than 5 percent oil per barrel of produced water (water from `water_cut_pct`). The credit is from the Comptroller's certified price of the production month (2005 dollars); a month not published gives no credit |
| TX low-producing gas well (`tx_lp_gas`) | No more than 90 Mcf a day over the three months before, as the file holds them (the month itself when it holds none); not for a well whose `well_type` is oil (casinghead gas); the certified price of the month sets the credit |
| TX high-cost gas (`tx_hcg`) | A cost ratio is given, and the month is within 120 months of completion when a date is given; the rate by Sec. 201.057(c) |
| TX and LA two-year inactive wells | 24 months or more without production before the month: `inactive_months`, or the file's own run of zero months |
| LA stripper (`la_stripper`) | 10 bbl or less per producing day (`days_produced`, else the calendar days) |
| LA incapable oil (`la_incapable`) | 25 bbl or less per producing day with 50 percent salt water or more (`water_cut_pct`); not assessed without a water cut, and the row says so |
| LA incapable gas (`la_gas_incapable`) | Under 250 Mcf a day over the month's calendar days, for a well not designated an oil well |
| LA deep wells | True vertical depth over 15,000 feet, completed after July 31, 1994 when a date is given, within 24 months of completion (commercial production is assumed to begin then; payout is not in the file) |
| LA horizontal wells | `horizontal` yes, within 24 months of completion (18 for gas from a well completed on or after July 1, 2025); payout is not in the file |
| NM district (`nm_district`) | Not a reduction: the district's ad valorem production rate applied, or, without a district, the tax left out and the range of the 2026 districts stated. No reduced New Mexico rate is flagged (see below) |

**Potential savings** of a flag are the base tax less the tax with that rule alone. A well's potential savings take, for each month and product, the one flagged rule that saves the most, since reduced rates do not stack; the lease's are the sum over its wells, and the list shows the largest first. Not assessed from a file: Louisiana's low-pressure oil well gas (wellhead pressure), Texas enhanced recovery, flared and restimulated gas (Railroad Commission certification), and payout of any well.

**Tests:** `site/scripts/test-lease.mjs`, run by `tests/test_session45.py`: a three-well, two-month lease for each state worked by hand (base, with ticks, potential savings, fees and flags), each threshold from both sides, and no network call (fetch, XMLHttpRequest, WebSocket, EventSource and sendBeacon trapped while the sample is parsed, analysed and written; the page's sources name none of them).

## The refund finder (session 57, internal)

**Who it is for.** A severance tax consultant asks one question: which Texas leases may be paying more severance tax than the rules require, and how much might they save? The page is `/severance/finder`, behind the internal token (404 without it).

**The data.**
- The Railroad Commission of Texas's Production Data Query dump, already on disk from session 49 (no new download).
- Its table OG_COUNTY_LEASE_CYCLE, streamed once and split by county for the latest 48 production months (`warehouse/connectors/rrc_statewide.py`).
- `rrc_lease_production_statewide` holds the latest 24 months, partitioned by county. It also carries the wells the RRC lists on each lease (OG_WELL_COMPLETION) and those with no shut-in date at the extract.
- **License: internal** (the RRC grants no reuse in writing). It is not in git, the public database, public Redivis or any committed JSON.

**The tests** (`warehouse/derived/severance_screen.py`). Each lease is tested month by month over the 24 months, with the rules and citations of `site/data/severance_rules.json`. A lease reported in several counties is tested once, on its sum.

| Rule | The test the data can make | The money |
|---|---|---|
| Low-producing oil lease credit (`tx_lp_oil`) | under 15 bbl per well per day over the months of the 90 days ending with the month, divided by the wells listed and not shut in (at least one) | the certified price's credit; no certified price in the rules file, no credit |
| Low-producing gas well credit (`tx_lp_gas`) | a gas lease (one gas well) at 90 Mcf a day or less over the three months before (the months with a filed report; the month itself when none) | the certified price's credit |
| Two-year inactive well (`tx_oil_inactive`, `tx_gas_inactive`) | producing after 24 months or more without production, having produced before; see the two cases below | 0 percent of value |

**The two cases of the two-year inactive test:**
- **Seen:** the production before the gap is in the 48 months read. The saving is estimated on at most the lease's average producing month of the 12 before the gap, because new wells drilled on the lease are not exempt.
- **Older:** the gap runs back past the 48 months, and the RRC's first month for the lease (OG_SUMMARY_ONSHORE_LEASE) is at least 12 months older. The lease is flagged with no saving estimated.

A lease whose first RRC month falls inside the gap is new, not inactive. The first run flagged such leases (new Permian leases report zeros before their first well produces) and was corrected.

**Prices.** Monthly means of EIA's daily spot prices: WTI Cushing per barrel for oil and condensate, and Henry Hub per MMBtu for gas, applied per Mcf as if one Mcf held one MMBtu. These are labeled, and they are not the operator's prices. Base rates: 4.6 percent of value for oil and condensate, 7.5 percent for gas.

**How the finder differs from the lease tool:**
- The oil test divides by the RRC's well count, where the lease tool reads a real lease as one well.
- The inactive run counts unfiled months as months without production.

`site/scripts/test-finder.mjs` runs a gas lease and a one-well oil lease through the lease tool. Their months, base tax and saving agree with the finder to the cent.

**What no flag can see:**
- certification and the forms: AP-216 and AP-217, and the Commission's designation;
- filings already made: a credit already claimed is not in the dump;
- per-well volumes: the RRC reports leases;
- water (the oil test's other branch), flared gas, and high-cost gas already reported;
- the operator's own prices.

A flag means a lease **may** qualify, never that it qualifies. Not tax advice.

**Louisiana (Part B of session 57) was not built.**
- **The terms:** the SONRIS disclaimer of the Department of Conservation and Energy (formerly DENR) states the data is "for general informational purposes only" and disclaims warranty and liability. It grants no reuse, so the license would be internal.
- **The access:** SONRIS's parish and lease production reports sit behind a CAPTCHA. The CAPTCHA-free legacy report takes one field, one operator and one month per request. A parish's 24 months would mean thousands of requests, in effect working around the CAPTCHA, so no request was made for production data.
- **Next step:** a bulk extract from the department.

## Left out: no page read states them

**Texas:**

- the Railroad Commission's certification terms (its rules, Title 16 of the Texas Administrative Code, were not read);
- the late-application cut in high-cost gas (Sec. 201.057(f), a 10 percent reduction for a late filing), which the calculator does not model;
- the Comptroller's marketing-cost policy for gas (the page "Audit Policy on Natural Gas Marketing Costs" was not read), so no deduction is computed;
- the statute text of Tax Code chapters 201 and 202.

**Louisiana:**

- the oilfield site restoration fee (R.S. 30:87, amended by Act 662 of 2026), which is a fee, not severance tax;
- the posted field price comparison;
- the natural gas liquids rules beyond the gas rate.

**New Mexico:**

- rates from September 2026: TRD's table for 2026-27 was not yet published;
- the rule that sets the conservation tax at 0.19 or 0.24 percent (the table shows 0.24 for oil from April 2026);
- any price-based change in the emergency school or severance tax;
- New Mexico's reduced rates for stripper wells, enhanced recovery or well workovers (the NMSA text, on NMOneSource, could not be read as text);
- products H and C of TRD's table, which the table does not name;
- the equipment ad valorem tax.
