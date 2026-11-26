# The severance tool: the model audited as a hostile expert would

Session 10207, 26 November 2026, chain 710 (part D), the old laptop. Read as a state tax analyst who audits production tax returns, and as a mineral-rights economist who values royalty and working interests, each looking for the figure or sentence that is wrong. In the form of `docs/reviews/datacenter-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its folder of evidence (`docs/reviews/severance-model-audit-2026-11-26/`). No table written, no lock taken, no default moved, no model called, no request to any service.
- Each finding's test is on its own branch, `wip/audit-severance-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure carries the test only and is not for landing.
- Earlier reads are cited, not repeated: the faults of 16 November (`docs/reviews/severance-faults-2026-11-16.md`, "the faults file"), the reader's read of 16 November (`docs/reviews/severance-read-2026-11-16.md`, "the read"), and the ruling files of 17 November (`docs/reviews/ruling-impact-severance-2026-11-17.md`, `ruling-alternatives-severance-2026-11-17.md`, "the impact file").

## In short

- **The arithmetic is right.** An independent restatement written from the method note in exact decimals, not from the page's code, gives every figure of the default view from the page's own files to the cent: WTI Cushing's October 2026 mean of 22 days, 102.066364, rounded to USD 102.07; 1,000 bbl of Texas oil, gross USD 102,070.00, tax USD 4,695.22, savings USD 0.00, the clean-up fee USD 6.25; and the 17 rates, fees and certified prices of "Every rule, with its source". 907 figures and printed strings, 108 cases (every state, product, option, completion and New Mexico district), agree with the page's library (the largest gap 2.2e-16 relative). The published replication passes 612 of 612 on the same files.
- **The page prints Louisiana's floor and does not apply it (finding 1).** Under the table: oil is taxed on "the higher of the first purchaser's gross receipts less trucking, barging and pipeline fees, or the posted field price". The code takes the receipts less the fees typed and nothing else; no posted price is held. Fixed in words.
- **The lease tool taxes every month since 2023 at today's rules, unsaid (finding 3).** Louisiana's gas rate and horizontal exemptions for July 2026 to June 2027 and New Mexico's table for April to August 2026 are applied to a 2024 month as to an August 2026 one. The size needs the past rates, which no file here holds (a data request). Fixed in words.
- **Louisiana condensate takes the transport deduction the statute does not give it (finding 2).** The cited text taxes condensate at "twelve and one-half percent of gross value"; the deduction's own quote names oil. At USD 2 a barrel, 1,000 bbl owe USD 250.00 less (-1.96 percent); the page's own sample lease, USD 14.63 less. A figure: for Samuel's ruling.
- **"County levies are not here", yet New Mexico's district levy is (finding 4).** Its ad valorem production tax is a county district's rate; left out by default it puts a New Mexico total 13.6 to 19.5 percent low, and with it the New Mexico total holds a local levy that the Texas and Louisiana totals here do not. Fixed in words.
- **"Texas condensate owes 4.6 percent with no floor" (finding 5).** The rules file's own quote of Sec. 201.055(b) taxes condensate at the oil rate of Sec. 202.052, which has the 4.6-cent floor. It acts only below USD 1 a barrel. Fixed in words.
- **What an expert's own number would hold:** the price at the well, not at Cushing or Henry Hub (Texas's first purchase price is 0.6 to 1.6 percent under WTI over a fiscal year; Louisiana's and New Mexico's are not held); the gas's heat content and liquids (+3.40 percent at 1,034 Btu, liquids not sized); a twelve-month price, not one month's (WTI's twelve-month mean puts the default tax 19.6 percent lower, Henry Hub's 19.7 percent higher).
- **Four branches fix words and move no figure (1, 3, 4, 5); one shows a figure for ruling (2).** Two data requests.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/severance/page.tsx` | The page: the two tabs, the calculator's lead, the default prices (`latestMonthMean` of WTI Cushing and Henry Hub), the calculator, "Every rule, with its source" (each base rate, option, fee and the latest certified price, with links), the decisions fold, the downloads |
| `site/app/severance/Calculator.tsx` | The calculator (client): state, product, volume, price, Louisiana's completion and transport, New Mexico's royalty, trucking and district, one reduced rate, Texas's oil credit, the report period; the table (gross, taxable, each base line, base total, the options' effects, the total with them, savings, fees) and the state's basis note under it |
| `site/app/severance/Decisions.tsx` | The 14 decisions at the foot of both tabs, each with its default and source in a tip |
| `site/app/severance/lease/view.tsx`, `LeaseTool.tsx` | The Lease tab: its lead and promise, the monthly means since January 2023, the file reader, the cards, the flags and the lines |
| `site/lib/severance.ts` | All the tax arithmetic (`compute`, `creditPct`): gross, the deductions, each base tax, the floor, one reduced rate by its kind, the credit, savings, fees. No imports |
| `site/lib/lease.ts` | The lease file: columns, parsing, well facts, the "may qualify" tests, the best flag, the ticks; it calls `compute` |
| `site/lib/leaseprices.ts` | The default prices: `latestMonthMean` (the calculator) and `monthMeans` (the Lease tab), from `eia_fuel_spot_prices` through `lib/data.ts` |
| `site/data/severance_rules.json` | The rules, version 2026-09-30.2: 3 states, 7 products, each base rate, fee, option, threshold, certified price and New Mexico district with the passage that states it and its source |
| `site/app/severance/finder/`, `lease/real/`, `site/lib/finder.ts`, `rrclease.ts`, `warehouse/derived/severance_screen.py` | The internal refund finder and "Load a real lease" on the Railroad Commission's tables (internal license): not public, not restated here |
| `eia_fuel_spot_prices` | The only table the public tool reads: EIA's daily WTI Cushing (RWTC) and Henry Hub (RNGWHHD). Read here from the main copy's `warehouse/output/` (retrieved 13 November 2026, rows to 11 November 2026) |
| `docs/methods/severance.md` | The method note: sources, each state's rules, the calculator's steps, the lease tool, the finder, "Left out", the decisions table, the cross-check |
| `replication/severance/` | `replicate.py` (612 of 612 here), `crosscheck.py` and `crosscheck.json` (the publishers' pages and Texas's collections), `cases.json`, the sample lease |

## How every number here was computed

- **The default view:** `/severance` as drawn on 26 November 2026 (the instant 2026-11-26T12:00Z): Texas, oil, 1,000 bbl, the default price, nothing ticked, no deduction.
- **The independent restatement:** `restate.py` (standard library, `Decimal`), written from the method note's "How a figure is computed" and "Default prices": the read from the first day of the month three months back, the latest complete month, the mean rounded half up to the cent, then steps 1 to 8 for every case.
- **The page's own code on the same files:** `lib_figures.mjs` runs `lib/leaseprices.ts` and `lib/severance.ts` with the live set's one request answered from the CSV, draws `Calculator.tsx` and the whole of `page.tsx` (default tab) to HTML with the site's own loaders (`register.mjs`; `brand-stub.mjs` draws `components/Brand.tsx`, which imports Next's fonts, as a plain wrapper), and keeps the visible text. `compare.py` sets the two side by side and checks each printed string.
- **One rule at a time:** `measures.py`, on the restatement's arithmetic; the cross-check's Texas collections (`crosscheck.json`) and EIA's heat content (`site/data/forecast/gas.json`, 1,034 Btu a cubic foot).
- Copies of every script and its printout: `docs/reviews/severance-model-audit-2026-11-26/` (written to run from `runs/c10207/` of a worktree; the drawn HTML of the calculator and the page beside them).

## The arithmetic re-done

| Figure the default view prints | The page | Restated | Gap |
|---|---|---|---|
| Default price, oil | "WTI Cushing, the mean of 22 daily EIA spot prices in 2026-10, $102.07 per barrel" | 2026-10, 22 days, 102.066364, to the cent 102.07 | 0 |
| Default price, gas (shown when gas is chosen) | 2026-10, 22 days, $2.99 per MMBtu | 2.987727, 2.99 | 0 |
| Gross value | $102,070.00 | 102,070.00 | 0 |
| Oil production tax, 4.6% | $4,695.22 | 4,695.22 (the floor, USD 46.00, does not act) | 0 |
| Tax at the base rate; with the exemptions chosen; savings | $4,695.22; $4,695.22; $0.00 | the same | 0 |
| Oil Field Clean-Up Fee | $6.25 | 6.25 | 0 |
| "Every rule, with its source": 17 rates, fees and certified prices | e.g. 4.6%, 7.5%, $0.1514 per Mcf, 12.5%, 3.75%, 3.15%, 0.24%, 4%, 0.19%, $0.00625 and $0.000667 a unit, $53.55 and $1.36 for 2026-08 (2005 dollars) | the rules file's | 0 |
| Rules version | 2026-09-30.2 | the file's | 0 |

- **907 checks:** the two default prices; 108 cases (each state and product at 1,000 units, both Louisiana completions, every option alone at its default, the oil credit, all 35 New Mexico districts for oil and gas, a Jal well with a one-eighth royalty and USD 1 trucking, Louisiana oil and condensate with USD 2 transport), each with gross, taxable, every base line, base total, total with options, savings and fees; 25 printed strings. Every number equal to the cent and to 1e-9 relative (the largest gap 2.2e-16).
- **The replication** (`replication/severance/replicate.py`, the same CSV, the same instant): 612 of 612 inside half the last shown digit, 37 of 37 word keys the same.
- **Rounding:** each cent of the page (JavaScript's rounding of its float) equals the restatement's half-up rounding of the exact decimal in every case.

## One rule changed at a time

Each line changes one choice and keeps every other. The default case is Texas oil, 1,000 bbl, USD 4,695.22 of tax, unless the line names another.

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| The latest complete month's mean (October 2026, WTI 102.07, Henry Hub 2.99) | the twelve months' mean, November 2025 to October 2026 (WTI 82.02, Henry Hub 3.58) | Texas oil USD 3,772.92 (-19.6 percent); Texas gas, 1,000 Mcf, USD 224.25 to 268.50 (+19.7). The twelve monthly means run from 57.97 to 102.13 (oil) and 2.77 to 7.72 (gas) | yes: the month is named beside the box |
| The same | November's eight days held (WTI 93.69, Henry Hub 2.74) | -8.2 percent (oil), -8.4 percent (gas) | yes |
| The mean rounded to the cent, then taxed | the unrounded mean | USD 4,695.22 against 4,695.05 | the read, row 13; the impact file, line 5 |
| WTI Cushing for Texas oil | Texas's first purchase price (EIA), over a fiscal year | the cross-check's statewide totals: WTI is 1.62 percent above (fiscal 2025) and 0.55 percent (fiscal 2026) | "a hub price is not the value at the well" |
| One Mcf as one MMBtu | 1,034 Btu a cubic foot (EIA, the rule `/impact` uses) | Texas gas USD 224.25 to 231.87 (+3.40 percent); New Mexico 237.41 to 245.48 (+3.40); Louisiana, per Mcf, unchanged | yes (decision 2); the impact file, line 3 |
| Louisiana oil completed before 1 July 2025 (12.5 percent) | on or after (6.5 percent) | USD 12,758.75 to 6,634.55 (-48.0 percent) | yes (decision 7) |
| Louisiana condensate takes the transport deduction | gross value, as the statute says | at USD 2 a barrel, USD 12,508.75 against 12,758.75 (+250.00, +2.0 percent without the deduction); the sample lease +14.63 | no (finding 2) |
| Louisiana's value: receipts less transport | the higher of that and the posted field price | not sized: no posted price is held | no (finding 1) |
| New Mexico with no district: ad valorem left out | the median of the 35 districts (1.249 percent); the highest (1.7249) | oil USD 7,287.80 against 8,562.65 (-14.9 percent) and 9,048.40 (-19.5); gas 237.41 against 274.75 (-13.6) and 288.98 (-17.8) | yes, the line says "left out"; finding 4 for what it is |
| New Mexico oil's conservation rate 0.24 percent (TRD's table from April 2026) | 0.19 percent (the gas rate; the rule that sets each was not read) | -USD 51.04 on 1,000 bbl | the method note's "Left out" |
| No royalty deducted in New Mexico by default | a federal lease's one-eighth | USD 7,287.80 to 6,376.82 (-12.5 percent) | yes, the box |
| The latest certified period held, August 2026 | September 2026, published since (oil USD 48.59, gas 1.23) | the calculator: 0 (both stay in the same tier, oil none, gas 100 percent); the Lease tab: a September gas month gets no credit where the rule gives 100 percent | the faults file, row 2 |
| Texas oil's floor, 4.6 cents a barrel | none | 0 at any price over USD 1 a barrel, so on every month since 2023 | yes (decision 3) |
| Rules of one date for every month (the Lease tab) | each month's own rates | not sized: the past rates are not held (data request 2) | no (finding 3) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| The tax base, gross against net | the lead, the basis notes, decision 9 | Texas: volume x price, no deduction (marketing costs said not read). Louisiana oil and condensate: gross less volume x the transport typed. New Mexico: gross less the royalty share and the trucking typed. Never below zero | Texas and New Mexico **right as stated**. Louisiana: the floor of the posted price is printed and not applied (**finding 1**); condensate takes a deduction its statute does not give (**finding 2**) |
| Wellhead price against a hub | the line under the price box, decision 1 | WTI Cushing and Henry Hub, monthly means, editable | **Right as stated**: "a hub price is not the value at the well, which is what the states tax". The sizes are in the table above; Waha and the states' first purchase prices are the read's rows 11 and 12 |
| Gas per Mcf at a price per MMBtu | the label, decision 2 | 1 Mcf = 1 MMBtu | **Right as stated**; its worth, +3.40 percent at EIA's heat content, waits on the impact file's line 3 |
| Volumes: source and year | the calculator's volume box | The reader's, one month; nothing read | Not a figure of the ERW; the read's row 9 holds the share |
| Rates and their dates | "Every rule", each line's "effective"; decisions 7, 8, 10 | One rules file read on 30 September 2026; the calculator takes no month, the Lease tab applies the same rates to every month of a file | Calculator: the dates are printed beside each rule, **right**; the default month (October 2026) lies outside New Mexico's table (the faults file, row 5). Lease tab: **finding 3** |
| Exemptions and their dates | the options' "who", "what", "how long" | Each applies in full when ticked; no window, payout or cap is tracked in the calculator; the Lease tab tests windows from the completion date | **Right as stated**: the 50 percent cap of high-cost gas and payout are said not tracked (decision 6, the lead of the Lease tab) |
| Nominal against real dollars | the certified prices; the default price | Certified prices in 2005 dollars, compared only with the tiers' bounds (also 2005 dollars); the typed price, nominal, is never compared with them | **Right as stated**: "(2005 dollars)" beside each certified price, "never by the price typed" (decision 5) |
| Forecast against reported | the lead ("for education and planning") | Nothing is forecast: a reported month's mean and published rules | **Right**; one month's mean stands for any month, and its worth is in the table above |
| Comparisons across states | the state list | No comparison is printed; switching state keeps volume and price | No claim made. Effective rates at the default prices: Texas oil 4.6, Louisiana 12.5 (6.5 for a new well), New Mexico 7.14 (8.39 with the median district); gas 7.5, 5.06 (a tax per Mcf: 1.96 to 5.47 percent of value over the twelve months) and 7.94 (9.19). A reader who sets them side by side meets **finding 4** |
| "Every rate, exemption and threshold cites the statute or state agency page whose text states it" | the lead | Each rule carries its quote and source | **Right**, with two exceptions the page does not mark: Texas condensate's floor (**finding 5**: the cited section states one, the page says none is owed) and Louisiana condensate's deduction (**finding 2**: the cited text says gross value) |
| "Deductions ... computed only where the state's rule states them (Louisiana's transport charges on oil ...)" | the lead | Louisiana's deduction on oil and on condensate | Oil **right**; condensate is **finding 2** |
| "Local taxes, county levies and federal royalties are not here" | the lead | New Mexico's ad valorem production tax at the district's rate is a base line when a district is chosen | **Finding 4** |
| "Texas condensate owes 4.6 percent with no floor per barrel" | decision 3 | No floor for condensate | **Finding 5** |
| One reduced rate a well and month; the oil credit stacks | decision 4 | One rate option replaces the first base tax; the credit multiplies the total after it | **Right**; the code also lets the credit stack with the two-year inactive exemption, which the Comptroller does not list, but that tax is already 0, so no figure moves |
| The certified price sets the credit | decision 5, the tip of the report period | The first bound the period's price is over | **Right**; every certified oil price held is over USD 30 (no credit), every gas price under 2.50 (100 percent) |
| High-cost gas: 7.5 less 7.5 x ratio / 2, never below zero | decision 6 | `max(0, rate - rate x ratio / 2)` | **Right**: Sec. 201.057(c) as the rules file quotes it |
| The stripper well's USD 20 test | the option's "what" | Taxable value per barrel (after transport) under 20 | **Right**: the statute's "average value set forth in Subparagraph (a)" is the value after the fees |
| No tax rounded on its own | decision 11 | Not rounded until display | **Right as stated**; a return may differ by a cent or two |
| The window the figures cover | the line under the price box; the rules version | The month of the default price is named; the rules' read date is not on the calculator's face (only "Rules version 2026-09-30.2" and each rule's effective dates) | **Right** for the calculator; for the Lease tab, **finding 3** |

## What a state tax analyst's or mineral economist's own number would hold that this does not

| Item | Size | From |
|---|---|---|
| The price at the well: Texas's first purchase price against WTI | -1.6 percent (fiscal 2025), -0.6 percent (fiscal 2026) on the tax | the cross-check's statewide totals |
| The same for Louisiana and New Mexico crude (Louisiana's light sweet often sells above Cushing, the Permian's at Midland near it) | not sized | no Louisiana or New Mexico first purchase price held: data request 1 |
| Gas at its heat content | +3.40 percent of every tax on value | EIA's 1,034 Btu a cubic foot |
| Gas liquids in wet gas (taxed with the gas's market value), Waha for Permian gas | not sized | no liquids price or Waha price held (Waha needs a license: the read, row 11) |
| A year's price, not one month's | WTI: -19.6 percent; Henry Hub: +19.7 percent on the default tax | the twelve monthly means held |
| New Mexico's district | +13.6 to +19.5 percent of a New Mexico total | the rules file's 35 districts |
| Rates in force in the month taxed (Lease tab) | not sized | data request 2 |
| Louisiana's posted field price as a floor | not sized | no posted price held |
| Marketing and post-production costs (Texas gas), exempt royalty interests, Louisiana's and New Mexico's fees, Texas's and Louisiana's local property taxes on wells | not sized | no rule read, no table held (the method note's "Left out"; the faults file, row 7, for collections) |

## Findings, largest effect first

| # | Severity | Finding | Effect | Fix | Branch |
|---|---|---|---|---|---|
| 3 | Medium | The Lease tab taxes every month of a file, back to January 2023, at the rates held today; never said | not sized (data request 2) | words | `wip/audit-severance-3` |
| 1 | Medium | Louisiana's floor (the posted field price) is printed under the table and not applied | not sized (no posted price held); any transport typed lowers the tax without a floor | words | `wip/audit-severance-1` |
| 2 | Low | Louisiana condensate takes the transport deduction; the cited statute taxes condensate on gross value | -USD 250.00 on 1,000 bbl at USD 2 a barrel (-1.96 percent); -14.63 on the sample lease | figure: ruling | `wip/audit-severance-2` |
| 4 | Low | "County levies are not here", yet New Mexico's district levy is; its default leaves it out | a New Mexico total 13.6 to 19.5 percent low without it | words | `wip/audit-severance-4` |
| 5 | Low | "Texas condensate owes 4.6 percent with no floor"; the cited section carries the floor | 0 above USD 1 a barrel | words | `wip/audit-severance-5` |

- Two Medium, three Low. Only finding 2 would move a figure if fixed.

## 1. Louisiana's floor is printed and not applied (Medium)

- **Where.** `site/data/severance_rules.json`, Louisiana's `basis_note` (printed under the calculator's table) and `value_deduction`; `site/lib/severance.ts`, `compute` (`taxable = gross - volume x transport`); decision 9; the method note, Louisiana and "Left out" ("the posted field price comparison").
- **Why it is wrong.** The note under the table says oil and condensate are taxed on "the higher of the first purchaser's gross receipts less trucking, barging and pipeline fees, or the posted field price". The code takes the first and never the second; the page holds no posted price. A reader who types the transport fees gets a tax that can be below the state's floor and is told the rule was applied. The method note says the comparison is left out; the page does not.
- **The test.** `tests/test_audit_severance_1.py` on `wip/audit-severance-1`: through `lib/severance.ts`, Louisiana oil with a transport fee equal to the price owes USD 0.00 (no floor acts; passes on main); the words test fails on main.
- **The fix on the branch, words only.** Decision 9 adds "Louisiana's floor, the posted field price, is not held, so its value here is the price typed less the fees typed, which can be below the value the state taxes."; the method note's step 2 says the same. No figure moves.

## 2. Louisiana condensate takes a deduction its statute does not give (Low; a figure)

- **Where.** `site/data/severance_rules.json`, Louisiana `value_deduction.products` (`oil`, `condensate`), its quote ("the value of oil shall be the higher of ..."), and the condensate rule's quote ("twelve and one-half percent of gross value at the time and place of severance"); `compute`.
- **Why it matters.** The deduction's own quote names oil; the condensate rule's names gross value. The lead says the transport charges are computed "on oil"; the decisions and the basis note say "oil and condensate". A reader who types transport for condensate pays 12.5 percent of it less than the cited text gives.
- **How much.** 1,000 bbl at USD 102.07 and USD 2 a barrel: USD 12,508.75 against 12,758.75 (-250.00, -1.96 percent). The page's own sample lease (well FICTIONAL-LA-2, 78 bbl over July and August 2026 at USD 1.50): -14.63.
- **The test.** `tests/test_audit_severance_2.py` on `wip/audit-severance-2`: the deduction lists condensate, its quote names only oil, the condensate rule's quote says gross value, and the code's condensate tax falls by exactly 12.5 percent of the transport. Not for landing.
- **For Samuel's ruling.** Default "left as it is". The other choice: no deduction for Louisiana condensate (the products list `oil` alone in the rules file, which the data machine keeps, since `/impact` and the finder read it too); then the lead's "on oil" is right as it stands.

## 3. The Lease tab taxes every month at today's rules (Medium)

- **Where.** `site/app/severance/lease/view.tsx` (the lead: "on the same cited rules as the calculator"); `site/lib/lease.ts` (every line through `compute` with the one rules file; the month sets only the price and the Texas certified period); `site/lib/leaseprices.ts` (`monthMeans` since January 2023).
- **Why it is wrong.** The tab prices any month since January 2023 and says nothing of which month's rates it applies. It applies the rules file's: Louisiana's gas rate of 15.14 cents for July 2026 to June 2027 (the rules file's own quote: "adjusted annually on July first"), the horizontal well shares of fiscal 2027 (80 percent for oil, 100 for gas, each set from a price each July), and New Mexico's table for April to August 2026, to a 2024 month as to August 2026. Texas's certified prices are the one rule read by month (a month before January 2025 earns no credit, and the tab says so).
- **How much.** Not sized: the past rates are in no file here (data request 2).
- **The test.** `tests/test_audit_severance_3.py` on `wip/audit-severance-3`: a Louisiana gas well's January 2024 month and its August 2026 month are taxed at the same 15.14 cents an Mcf by the lease tool (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The tab's lead adds "Every month of a file is taxed at the rates the rules file holds today: Louisiana's gas rate and horizontal well shares for July 2026 to June 2027, New Mexico's table for April to August 2026. A month outside those may have owed at another rate; only Texas's certified prices are read month by month."; the method note's lease section says the same.

## 4. "County levies are not here", and New Mexico's is (Low)

- **Where.** `site/app/severance/page.tsx`, the lead ("Local taxes, county levies and federal royalties are not here"); the New Mexico district list and line; decision 10.
- **Why it is wrong.** New Mexico's Oil and Gas Ad Valorem Production Tax is levied at the rate of the production unit's county district (35 rows, 0.7105 to 1.7249 percent). When a district is chosen it is a base line of the total; by default it is left out and the line says so. So the lead's sentence is false for New Mexico, and a New Mexico total with its district holds a local levy that a Texas or Louisiana total here never does. A reader comparing the states at the defaults sees New Mexico 13.6 to 19.5 percent low; with the district, the comparison is not like for like the other way.
- **The test.** `tests/test_audit_severance_4.py` on `wip/audit-severance-4`: the New Mexico total with a district less the total without it is the district's rate times the taxable value (passes on main); the words test fails on main.
- **The fix on the branch, words only.** The lead reads "Local taxes and federal royalties are not here, with one exception: New Mexico's ad valorem production tax, levied at the rate of the production unit's county district, is in the total when a district is chosen. A Texas or Louisiana total here holds no local tax."

## 5. Texas condensate's floor (Low)

- **Where.** `site/app/severance/Decisions.tsx`, decision 3 ("Texas condensate owes 4.6 percent with no floor per barrel"); the rules file's condensate `code` quote (Sec. 201.055(b): "at the same rate as the rate of the tax imposed on oil by Section 202.052"); the method note's Texas table.
- **Why it is wrong.** The decision states what condensate owes. The section the rules file quotes taxes it at the oil rate, which is "4.6 percent of the market value ... or 4.6 cents for each barrel ..., whichever rate results in the greater amount of tax". The calculator's choice (no floor, since the Comptroller's page states none) is a choice, not the law.
- **How much.** Nothing above USD 1 a barrel: no month since 2023.
- **The test.** `tests/test_audit_severance_5.py` on `wip/audit-severance-5`: at USD 0.50 a barrel, 1,000 bbl of Texas condensate owe USD 23.00 and oil USD 46.00 (passes on main); the words test fails on main.
- **The fix on the branch, words only.** Decision 3 reads "Texas oil owes 4.6 percent of market value or 4.6 cents a barrel, whichever is greater. Texas condensate is taxed here at 4.6 percent with no floor per barrel, since the Comptroller's page states none, though Sec. 201.055(b) taxes it at the oil rate, which has the floor. The floor acts only below USD 1 a barrel."; the method note's row follows.

## The decisions block, line by line

1. A hub price stands for the value at the well: **right as stated**; worth measured above.
2. One Mcf as one MMBtu: **right as stated**; +3.40 percent at 1,034 Btu.
3. Texas oil's floor; none for condensate: oil **right**; condensate **finding 5**.
4. One reduced rate, the oil credit stacks: **right**.
5. The certified price, 2005 dollars: **right**; September 2026 is published since (the faults file, row 2).
6. High-cost gas by cost ratio, the cap not tracked: **right as stated**.
7. Louisiana oil by completion date: **right**; -48.0 percent for a new well.
8. Louisiana gas by volume at the year's rate: **right** for July 2026 to June 2027; the Lease tab's other months, **finding 3**.
9. Deductions only where the rule states them: **findings 1 and 2**.
10. New Mexico's district: **right as stated**; what it is, **finding 4**.
11. No tax rounded on its own: **right as stated**.
12. Texas's fees apart: **right**.
13. A flag is the file's numbers against a threshold: the replication's sample lease, right.
14. A gas well's three months before: the replication, right.

## Not covered, or left open

- **The refund finder and "Load a real lease"**: internal tables, not on this machine in full; not restated (the faults file, row 4).
- **New Mexico's "AD /2" column read as the production rate** (the rules file's note): TRD's own Total Rate equals the sum on every row (the method note); the spreadsheet itself was not read here, and neither was the assessment ratio TRD's page names.
- **Louisiana's pressure base for an Mcf and Texas's**: not read; no web read was made.
- **Texas's exempt royalty interests and the late-filing cut of high-cost gas** (Sec. 201.057(f)): left out by the method note, not sized.
- **The pages in a browser**: the words branches were drawn to HTML with the site's own code and read (below); no layout, no width of 390 px.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-severance-1`, `-3`, `-4`, `-5`.
- **For Samuel's ruling, default "left as it is":** finding 2.
- **Data requests:** (1) EIA's crude oil first purchase prices for Texas, Louisiana and New Mexico, monthly; (2) the past rates: Louisiana's gas rate and horizontal well shares for each fiscal year July 2022 to June 2026, and TRD's New Mexico tables for each period from January 2023 to March 2026 and from September 2026.
