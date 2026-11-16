# Nine tools at the done line: a pack for Samuel (old laptop, 16 November 2026)

Energy Research Warehouse (ERW). Written by session 7522 of chain 304 (`queue/done/304-day-16-november-oldlaptop-done-line-economics.md`), samueloldlaptop, in the form of the trackers' pack (`docs/reviews/trackers-signature-pack-2026-11-16.md`). For each of the nine tools of part A: what you sign, the five choices that matter most, the cross-check in one table, the Stata run with what it should print, the whole replication's count, and the rulings with the default each stands on. Every figure below is copied from the tool's own files on its branch; none was computed for this pack.

- **Every page here is in review** (`site/lib/release.ts`: no page is live since session 166). Nothing in this pack opens a page, lifts a hold or publishes anything.
- **The work is on wip branches, not on main.** Each tool's branch is stacked on `wip/7500-done-line`, which is `wip/7200-large-load` (landing row 15, not landed) with origin/main merged. The data machine lands them from `docs/state/landing_request_oldlaptop.md`:

| # | Tool | Branch | Head | Landing row |
|---:|---|---|---|---:|
| 1 | `/contracts` | `wip/7501-contracts` | `f1417cfe7` | 18 |
| 2 | `/severance`, `/severance/finder`, `/severance/lease/real` | `wip/7502-severance` | `0580b9670` | 17 |
| 3 | `/shoulder` | `wip/7503-shoulder` | `179767c18` | 19 |
| 4 | `/battery/customer` | `wip/7504-battery-customer` | `76261ed94` | 25 |
| 5 | `/cost-of-power/battery/awards` | `wip/7505-battery-awards` | `74992ec65` | 20 |
| 6 | `/impact` | `wip/7506-impact` | `39fd3e028` | 21 |
| 7 | `/explore/ercot-peak-premium` | `wip/7507-peak-premium` | `a6184f8d2` | 22 |
| 8 | `/explore/demand-growth` | `wip/7508-demand-growth` | `39dc57835` | 23 |
| 9 | `/explore/interconnection` | `wip/7509-interconnection` | `aead62928` | 24 |

- **What a signature is.** You fill the note's sign-off lines and commit them, or say them in a prompt and a session writes your words there. A session never signs. Two of the nine notes carry a sign-off block today (the shoulder hours and the forecast tool); for the other seven the section a signature would go in is named, and a session adds the block in the form of `docs/methods/shoulder.md`, "Sign-off", on your word.
- **What you sign accepts** the rules and the defaults of the decisions. It does not freeze the figures: they move with the tables.
- **Before you run Stata.** A checkout that holds the tool's branch (main, once its landing row has landed). No do-file has been run: Stata is not on the machine that wrote them. Each was followed step for step by its Python mirror, whose printed lines are the expected values below. Run each from its own folder and keep a log, so a session can set your lines beside the mirror's.
- **The battery page, the generator page and the datacenter cost page** (part B, reads 10 to 12) are not in this pack; their state is in `docs/state/progress_c304.md`.
- **Order of the sitting.** One tool a sitting, in the table's order.

---

## 1. The contracts page (`/contracts`)

**You sign:** `docs/methods/contracts.md`. It has **no sign-off block**; a signature would go after its section 11, "The replication, and the faults found", accepting the views' rules (sections 3 to 7), the cross-check (section 8) and the nineteen decisions (section 9). The page and its eight tables are internal (FERC's terms unread: `www.ferc.gov` answered HTTP 403), so it draws nothing to a visitor. No party's name is in any file of this work.

**The five choices that matter most** (`site/app/contracts/Decisions.tsx`; the note's section 9, word for word):

| Choice | Default | Source |
|---|---|---|
| In force: a contract is in force when its row files no actual termination date | No actual termination date filed. For 2026 Q2: 178,842 rows in force, 8,031 terminated | FERC's contract file, the column actual_termination_date |
| Price as filed: the rate and its units when the filer gave a number, else the filer's own words | As filed. About half the rows give words | FERC's contract file: rate, rate_units, rate_description |
| Megawatts stated: only a quantity filed in MW, or in kW divided by 1,000 | MW and kW only | FERC's contract file: quantity and units (`eqr_terms.md`, "Megawatts, where a quantity is stated") |
| The megawatts ceiling: a row above the largest US power station is left out of the ranking and counted | 6,809 MW | EIA-860M, Inventory of Operating Generators, nameplate summed by plant |
| Buyer names: spellings counted together only when six rules leave them identical | The six rules, in order; no doubtful pair accepted yet. A buyer's count is a floor | `docs/methods/eqr_buyers.md`; FERC publishes no identifier for a buyer |

**Cross-check** (the note's section 8; no figure adjusted):

| Our figure | Published figure | Source | Difference | Why |
|---|---|---|---|---|
| Companies that file the report: 3,704 for 2025 Q3; 4,010 for 2026 Q2 (4,077 filings) | 3,672, "the total number of EQR filers as of Q2 2025" | FERC, Order No. 917, 91 FR 14306, footnote 354, 24 March 2026; the same count in the FERC-920 notice, 91 FR 7278, 17 February 2026 | +32 (0.9 percent) one quarter later; +338 (9.2 percent) four quarters later | ours counts company identifiers in FERC's file of each quarter; the quarter FERC counted is not held |
| The largest US power station: 6,809.0 MW | 6,809.0 MW | EIA-860M, inventory as of September 2026 | none | computed from the publisher's own inventory |
| Contracts by product; megawatts stated; prices as number or words; contracts new and gone; largest buyers and sellers | nothing published | | | FERC publishes the filings and no tally this project could read |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\contracts"
log using "contracts_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(Before it, once, from the repository's root: `python replication/contracts/copy_rows.py`, which writes `rows/contracts_slim.csv` from the internal table `ferc_eqr_contracts` in `warehouse/output`.)

**Expected**, on the table as retrieved on 4 October 2026 at 03:50 UTC (the filings for 2026 Q2, 186,873 rows):

- 1. contract rows filed for the quarter: 186,873
- 2. rows that file their rate as a number: 81,718
- 3. rows that file words and no number: 104,952
- 4. energy contracts in force: 22,808
- 5. energy contracts in force that state megawatts, and the megawatts: 356, 31,402.3
- 6. rows of energy, capacity and tolling executed in 2026 Q2: 227
- 7. tolling rows, and their contracts: 382, 217

**The whole replication** (`python replication/contracts/replicate.py`): **2,539 of 2,615 figures inside the tolerance, 76 named** (fault 7: the megawatts view's "place by contracts" is ranked another way than the largest view's, a data request), none unexplained; 785 of 785 words the same.

**Rulings, each with its default** (`docs/reviews/contracts-faults-2026-11-16.md` rows 8 to 13; `docs/reviews/contracts-read-2026-11-16.md` rows 18 to 22):

1. "MW filed" on the largest buyers and sellers adds every MW row with no ceiling, where the megawatts view leaves out rows above 6,809 MW. Default: left as filed, and the decision says it is the other count.
2. The list counts agreements by seller name and service agreement identifier; the other views count contracts by company identifier. Default: left, the decision states both.
3. With "Every product" chosen, 11 of the quarter's 25 balancing authorities are not in the panel. Default: left.
4. The page's explanations are grey notes, against the page standard. Default: left; what this chain added is on hover.
5. The license of the eight tables: FERC's terms pages answered 403. Default: the hold stands; a person reads them in a browser and rules.
6. Only two figures have a published figure to stand against. Default: said so in the note, nothing adjusted.
7. Capacity prices are listed in three units with no conversion. Default: as filed; the fold now says 1 $/KW-MO equals 1,000 $/MW-MO.
8. A rate filed as 0 counts as a price. Default: counted, and said.
9. An end date of 2099-12-31 draws a 73.7-year term. Default: as filed.
10. Rows whose buyer is a market operator are counted among contracts signed, and the catalog line says "bilateral". Default: counted, the fold says what they are; the word "bilateral" is left for you.
11. Sellers named for storage are counted (715) and cannot be listed. Default: no list entry added.

---

## 2. The severance tax tool (`/severance`, with `/severance/finder` and `/severance/lease/real`)

**You sign:** `docs/methods/severance.md`. It has **no sign-off block**; a signature would go at the end of its section "The tool as a reader meets it (session 7502, 16 November 2026)", accepting the views, the rules file, the fourteen choices and the cross-check. The finder and the real lease view are internal.

**The five choices that matter most** (the page's fold, `site/app/severance/Decisions.tsx`; the note's table "The choices that move a figure"):

| Choice | Default | Source |
|---|---|---|
| A hub price stands for the value at the well | the latest complete month's mean: WTI Cushing, Henry Hub | EIA daily spot prices |
| One Mcf is priced as one MMBtu | 1 to 1 | a choice of session 40 |
| A low-producing credit follows the certified price (2005 dollars) | the latest period held, August 2026 | the Comptroller's certified prices; Secs. 201.059(b), 202.058(c) |
| Louisiana oil by completion date | before July 1, 2025: 12.5 percent | La. R.S. 47:633 |
| New Mexico's ad valorem rate by district | not chosen: left out | TRD's table, April to August 2026 |

**Cross-check** (the note's "The cross-check (16 November 2026)"; `replication/severance/crosscheck.py`; no figure adjusted):

| Our figure | Published figure | Source | Difference | Why |
|---|---|---|---|---|
| Texas oil, gas and condensate rates, the two fees, the enhanced recovery rate | the same | Texas Comptroller, production tax pages, read 16 November 2026 | none | |
| Texas certified prices, January 2025 to August 2026: 20 periods each | the same 20, to the cent | Texas Comptroller, low-producing leases and wells pages | none | |
| The latest certified period: August 2026 | September 2026: oil USD 48.59 (no credit), gas USD 1.23 (100 percent credit) | the same pages | one period newer | the rules file was read on 30 September 2026 |
| Louisiana's rates and thresholds | the statute's words | La. R.S. 47:633 | none | |
| Texas oil production tax, fiscal 2025: USD 6,621,844,278 (4.6 percent of EIA's Texas production at EIA's first purchase price) | USD 5,383,668,225 | Texas Comptroller, Historical All Funds Revenue; EIA production and first purchase price | ours 23 percent above | condensate taxed under the gas tax, enhanced recovery at 2.3 percent, exempt royalty, cash collections |
| The same, fiscal 2026: USD 7,175,971,817 | USD 5,876,551,070 | the same | ours 22 percent above | the same |
| Texas natural gas production tax: USD 2,749,852,795 (2025); 3,531,268,715 (2026) | USD 2,479,282,624; 2,434,406,070 | the same workbook; EIA marketed production | 11 and 45 percent above | Henry Hub is not the wellhead price; high-cost gas and credits; theirs also holds condensate |
| New Mexico's rates; Louisiana's and New Mexico's collections | none to stand against; not read | | | said so |

What it says: the base rule on a hub price is a ceiling on what a state collects, not a forecast of it.

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\severance"
log using "severance_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(Before it, once: `python replication/severance/replicate.py --tables DIR --headline`, which writes `rows/spot_slim.csv` from the public table `eia_fuel_spot_prices` and prints the same six lines. For another day, set the do-file's local `month` to the month before the latest month the file holds.)

**Expected**, for a page drawn on 16 November 2026 (October 2026, 22 trading days of each series):

- default oil price, WTI Cushing, mean of 2026-10 (USD per bbl): 102.07
- default gas price, Henry Hub, mean of 2026-10 (USD per MMBtu): 2.99
- Texas oil, 1,000 bbl, tax at the base rate (USD): 4,695.22
- Texas gas, 10,000 Mcf, tax at the base rate (USD): 2,242.50
- Louisiana oil, 1,000 bbl, well completed before July 1, 2025 (USD): 12,758.75
- New Mexico oil, 1,000 bbl, no district chosen (USD): 7,287.80

**The whole replication** (`python replication/severance/replicate.py`): **612 of 612 figures inside the tolerance** (the calculator at its default and 46 named cases, the Lease tab's sample, four real leases by totals only). Not replicated: the refund finder (its three files are on the data machine only, data request row 3).

**Rulings** (`docs/reviews/severance-faults-2026-11-16.md` rows 6 to 8; `docs/reviews/severance-read-2026-11-16.md` rows 7, 13 to 16):

12. 30 grey notes on the two tabs, against the page standard. Default: left, counted.
13. "Tax at the base rate" read as what a state collects is 22 to 25 percent high for Texas oil. Default: said in the note, not on the page.
14. A lease of many wells is tested as one for the low-producing oil credit. Default: as it is.
15. The calculator holds one month's price; a reader working an earlier month types it. Default: the box is not tied to the report period.
16. `/learn/problems`, set D, questions 4 and 5 prices on the unrounded mean and differs from `/severance` by 17 to 86 cents. Default: `/severance` keeps its rule; the fix is in the problem sets' three files.
17. `/impact` prices an Mcf at 1,034 Btu a cubic foot where `/severance` uses one MMBtu (3.4 percent more tax on the same gas). Default: each page keeps its rule (`/impact` is under your own review).
18. `/impact`'s severance adds Texas's regulatory fee, which `/severance` draws apart (USD 31.02 on the same 46,500 Mcf). Default: left.
19. On the Lease tab one file is one lease. Default: as now; a `lease_id` column would test each on its own.

---

## 3. The shoulder hours (`/shoulder`)

**You sign:** `docs/methods/shoulder.md`, section "Sign-off". It accepts this note; `shoulder_hours.md`; `replication/shoulder/` (20,633 of 20,634, one rounding edge named; 22,092 of 22,092 from the hours); the cross-check of section 9; the 18 decisions of section 5. It leaves open the five items of section 10.

**The five choices that matter most** (`site/app/shoulder/Decisions.tsx`; the note's section 5):

| Choice | Default | Source |
|---|---|---|
| `level`: the shoulder is measured against net load's daily mean | the daily mean; the second measure uses the midpoint to the evening peak | session 75 |
| `end`: it ends when net load is back at the mean, cut at midnight when it never is | cut at midnight; in California every month, in Texas every month of 2026 and eleven of the twelve of 2025 | session 75 |
| `fleet`: the fleet is the batteries operating that month in EIA's inventory | EIA-860M operating units; a grid operator's own count is larger | `storage_buildout_monthly` |
| `covered-needed`: hours covered and hours needed | the batteries alone, at rated power, full at the start, no losses, no transmission limit | session 75 |
| `california`: California from two sources, never mixed | EIA-930 to November 2025; CAISO's own supply by fuel from June 2025 | session 80; `eia930_caiso_break.md` |

**Cross-check** (the note's section 9; no figure adjusted):

| Our figure | Published figure | Source | Difference | Why |
|---|---|---|---|---|
| ERCOT fleet, end of 2025: 13,909 MW | "more than 17,000 MW" | Potomac Economics, *2025 State of the Market Report for the ERCOT Electricity Markets*, June 2026, page ii | at least 3,091 MW lower (18 percent) | EIA-860M against ERCOT's own count of installed storage. Not adjusted: a ruling |
| ERCOT fleet MWh, end of 2025: 21,579 MWh | "31,500 MWh" | the same, page ii | 9,921 MWh lower (31 percent) | the same |
| ERCOT batteries' highest average hourly output, 2025: 2,606 MW at 19:00 | 2,390 MW | the same, page 23 | 216 MW higher (9 percent) | theirs is net injection; EIA-930's 2025 battery column held discharge only |
| California fleet, end of 2025: 15,760 MW | "over 17 GW" | CAISO Department of Market Monitoring, *2025 Annual Report on Market Issues and Performance*, June 2026, page 23 | at least 1,240 MW lower (7 percent) | EIA's inventory against the operator's count |
| California fleet, April 2026: 15,979 MW | "16 GW" | EIA, *Today in Energy*, 16 June 2026 | none at their rounding | the same inventory |
| California curtailment, 2024: 3,423,377 MWh | "3.4 million megawatthours" | EIA, *Today in Energy*, 28 May 2025 | none at their rounding | both are CAISO's count |
| The shoulder's length, hours covered, hours needed, the midday surplus | nothing published | | | "shoulder" is this page's own measure |

The other rows (the evening peak's hour in both grids, the fleet at the end of 2023 and 2024, prices the page does not hold) are in the note.

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\shoulder"
log using "shoulder_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(It reads `shoulder_hours_monthly` and `storage_buildout_monthly` as CSV from the folder in its line `global tables`, by default `../../warehouse/output`.)

**Expected**, on `shoulder_hours_monthly` as built on 4 October 2026 (27,201 rows) and the fleet as held on 3 October 2026; ERCOT, August 2026:

- 1. the evening shoulder, hours: 5 (from 19:00 to 24:00)
- 2. net load above its daily mean in the shoulder, MWh: 66,629.88
- 3. the fleet's hours at full power (MWh over MW), and the hours of the shoulder it covers: 1.65 and 1.65
- 4. hours the fleet would need to deliver all of it: 3.66
- 5. the same on the ten worst days of 2026, their mean: 6.58 (10 days)

**The whole replication** (`python replication/shoulder/replicate.py`): **20,633 of 20,634 inside the tolerance** over 193 views, the one outside named (ERCOT, September 2025, 61,089.58 against 61,089.5749, a rounding edge); `from_hourly.py`: **22,092 of 22,092** values of the table equal from EIA's hourly workbooks. After part B's changes: 21,353 of 21,354. Not recomputed from hours: California by CAISO's own data and California's battery output.

**Rulings** (the note's section 10; `docs/reviews/shoulder-faults-2026-11-16.md` rows 10 to 12; `docs/reviews/shoulder-read-2026-11-16.md` rows 11 to 14 and 17):

20. Which fleet: EIA-860M (13,909 MW) or the market monitor's (more than 17,000 MW). On the monitor's figures December 2025 needs 1.99 hours, not 2.43. Default: EIA-860M stays, the block names the difference.
21. The level: the shoulder ends at midnight in California every month and in Texas since 2025. Default: both measures stay, the first as the headline.
22. Grey notes drawn by the shared tool frame. Default: not changed here.
23. "The midday surplus" in Texas was mostly the night until mid 2024. Default: the rule and the name stay, with a tip where the low is before 08:00.
24. No A and B of two grids or two months. Default: not built.
25. "The ten worst days" rank the largest swing, not the tightest evening. Default: the rule and the word stay; each day now carries its peak.
26. "Hours needed" is the fleet's, not one battery's. Default: no input by duration.
27. Which demand California's shoulder stands on (EIA-930 counts the batteries' charging; the shoulder is 28 to 42 percent higher by CAISO's data). Default: both side by side.
28. "Fleet, MW" is written with decimals here and whole on `/storage`. Default: not changed here.
29. The yearly "Midday surplus" column for Texas 2019 to 2024 carries no mark. Default: none added.

---

## 4. What a battery saves a customer (`/battery/customer`)

**You sign:** `docs/methods/battery_customer.md`. It has **no sign-off block**; a signature would go after its section 11, "Tests" (before section 12, the part B read), accepting the arithmetic (section 3), the ten choices (section 5), the cross-check (section 7) and the replication (section 9).

**The five choices that matter most** (`site/app/battery/customer/Decisions.tsx`; the note's section 5):

| Choice | Default | Source |
|---|---|---|
| The hours the peak lasts (what comes off is the smallest of power, energy over the hours, and the peak) | 2 hours, changed in the field | None published: a starting value of session 88 |
| The battery knows when the peak comes and is full for it, every month | All of it comes off | A choice of session 88. NREL found about 85 percent of a 4 hour battery's power on 98 buildings' measured loads |
| The round trip | 86 percent, changed in the field | Lazard, *Levelized Cost of Energy+*, June 2025, page 43 (the low end of its range) |
| The days a month the battery runs | 21 days, changed in the field | The calendar: 2026 has 261 weekdays |
| The year is the month typed, twelve times | Twelve months alike | A choice of session 88 |

**Cross-check** (the note's section 7; no figure adjusted):

| Our figure | Published figure | Source | Difference | Why |
|---|---|---|---|---|
| Share of a 4 hour battery's power off the monthly peak: 1.00 | about 0.85 | NREL, Neubauer and Simpson, NREL/TP-5400-63162, January 2015, page 16 | ours 0.15 higher (18 percent); on the report's tariff USD 3,014.00 against USD 2,561.90 a month | the tool knows the peak; NREL ran a controller on measured loads |
| The same for a short battery: set by the hours typed (0.25 of a 30 minute battery's power off a 2 hour peak) | about 0.60 for a 30 minute battery under about 25 kW | the same report, page 9 | not one figure | the tool has no load shape |
| Peak saving against energy saving: 4.5 times on the report's tariff; 0.94 to 2.06 times on today's six time-varying cases | "the economic savings of demand charges dwarf the impact on energy costs, often by an order of magnitude or more" | the same report, page 9 | ours gives energy a far larger part | the tool cycles the whole battery daily; the 2013 tariff charged USD 30.14 per kW |
| Demand charges above USD 15 per kW: 3 of 9 cases | "Nearly 5 million commercial customers" of 18 million | NREL and Clean Energy Group, NREL/BR-6A20-68963, August 2017, page 1 | none to take | it places the cases |
| A customer's saving a year: USD 7,164 to USD 62,059 across nine cases | nothing published | | not comparable | no published bill saving for the same tariff, customer and battery |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\battery_customer"
log using "battery_customer_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(No table and no step before it: each case's nine numbers are typed in the do-file, as `cases.json` holds them.)

**Expected** (the Python mirror, `replicate.py --headline`, 16 November 2026):

- Seattle City Light, medium, City of Seattle, time of use: saved a year (USD): 12,795.06
- Seattle City Light, medium, Downtown Network, time of use: saved a year (USD): 21,732.89
- Salt River Project E-32, summer peak: saved a month (USD): 1,114.70
- Austin Energy, secondary voltage 10 to under 300 kW: saved a year (USD): 8,931.16
- Southern California Edison TOU-GS-2 B, summer 2013, as NREL prints it: saved a month (USD): 3,676.97

The page shows each to the whole dollar: $12,795, $21,733, $1,115, $8,931 and $3,677.

**The whole replication** (`python replication/battery_customer/replicate.py`): **331 of 331 inside the tolerance, 12 cases**; none named. Said by its writer: it had read the page's code first.

**Rulings** (`docs/reviews/battery-customer-faults-2026-11-16.md` rows 3 to 9; `docs/reviews/battery-customer-read-2026-11-16.md` rows 4 to 9; landing row 25):

30. "Saved a year" is twelve of the month typed: 52.3 percent over on Salt River Project's E-32 with July's rates. Default: the figure stays; the block gives the 52 percent on hover.
31. A battery larger than the building's use in the peak hours is credited its whole energy. Default: said in the block and the note.
32. The 2 hours of the peak field have no published source. Default: 2 hours stays, said so.
33. "From shaving the peak" is an upper bound (NREL's 85 percent). Default: the figure stays an upper bound.
34. 14 grey notes on the page. Default: left, counted.
35. One battery and one bill at a time, no A and B. Default: one case.
36. The summary says "lowers the bill by -$23" when the total is below zero. Default: as it is (the words are yours).
37. A rate under 5 typed in cents is taken as dollars (4.9 reads USD 70,169 a year). Default: the limit stays at USD 5 per kWh; the other way is USD 1.
38. Salt River Project charges "all kW over 5 kW"; the page's demand charge is USD 33.75 over the bill. Default: left.
39. Where the store's peak is outside the peak-rate hours the discharge is paid at the mid-peak rate. Default: left, as the fold says it.
40. `/learn/bill` has no demand charge for the manager it is linked for. Default: left (the portable laptop's tool).
41. What a battery earns does not link this page. Default: left for that page's read.
42. "Round trip" here, "Round-trip efficiency" on two other pages. Default: left.
43. Salt River Project's and Austin Energy's terms bar reproducing their materials without written permission; only their rates are kept, as cited figures. Default: kept; the fallback is to drop those five cases.

---

## 5. What Texas's batteries were awarded day-ahead (`/cost-of-power/battery/awards`)

**You sign:** `docs/methods/battery_awards.md`. It has **no sign-off block**; a signature would go after its section 7, "What the tool does not hold" (before section 8, the part B read), accepting the head of the page's rules (sections 2 to 4), the replication and cross-check (section 5) and the fifteen fixed decisions (section 6).

**The five choices that matter most** (`site/app/cost-of-power/battery/awards/Decisions.tsx`; the note's section 6; the page has no input, so none is editable):

| Choice | Default | Source |
|---|---|---|
| `fleet`: every Energy Storage Resource with a row in the month, awarded or not, out or testing included | every resource in the file | ERCOT, 60-Day DAM Disclosure Reports (NP3-966-ER) |
| `per-kw`: per kW of the sum of each resource's highest High Sustained Limit in the month | the highest limit, every resource | ERCOT's file, HSL; the EIA's 18,070 MW |
| `model`: the model beside the awards: one 2-hour battery, the day-ahead schedule, the hub average; whole months only | 2 hours, day-ahead, `HB_HUBAVG` | `battery_stack.md`; the market monitor's 17,000 MW and 31,500 MWh (about 1.9 hours) |
| `never-offered`: the model's figure times the share of limit-hours with no day-ahead offer: an allocation | the model's average | `ercot_storage_dam_offers.md` |
| `hub-price`: real-time energy, and charging, at the hub average's real-time price | `HB_HUBAVG`, each 15 minutes | ERCOT Nodal Protocols 6.6.3.1; NP6-905-CD |

**Cross-check** (the note's section 5; no figure adjusted):

| Our figure | Published figure | Source | Difference | Why |
|---|---|---|---|---|
| The fleet, December 2025: 16,392 MW; January 2026: 17,180 MW | "more than 17,000 MW and 31,500 MWh by the end of 2025" | Potomac Economics, *2025 State of the Market Report for the ERCOT Electricity Markets*, June 2026, page ii | at least -608 MW in December; +180 or less in January | each resource's highest day-ahead limit in the days held, against installed capacity at the year's end |
| The fleet, July 2026: 21,365 MW, 332 resources | 18,070 MW operating | EIA-860M as `storage_buildout_monthly` holds it | +3,296 MW (18 percent) | ERCOT lists a resource from the day it can be dispatched, testing included; over the EIA's MW every per kW figure would be 18 percent higher |
| Energy offered at USD 100 per MWh or less: 8.0 percent, January to July 2026 | "55% of energy offers were priced between $0-100 per MWh" in 2025 | the same report, page 24 | -47 points | real-time offers of 2025 against day-ahead curves of 2026 |
| Day-ahead ancillary share of the two markets: 20 percent, February to July 2026 | 24 percent from services, June 2025 | Modo Energy, 19 May 2026 (as held in `docs/methods/crosschecks/battery.md`) | -4 points | another period; ours leaves out real-time ancillary money |
| Revenue per kW: 7.17 USD over February to July 2026 | no figure for these months | the market monitor's report, page 22; Modo Energy, 19 March 2025 | none computed | six months against calendar years |
| The gap's three parts (9.70, 14.53, -0.62 USD per kW); the node spread; the share of resource-hours with an award (7.0 percent) | nothing published | | | the ERW's own arithmetic on ERCOT's disclosure |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\battery_awards"
log using "battery_awards_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(It reads `monthly_rows.csv` beside it, the 1,699 public rows the page reads, committed on the branch. After a new copy of the tables: `python replication/battery_awards/replicate.py --tables <dir> --write`.)

**Expected**, on the tables as retrieved on 5 October 2026 (the awards to 5 August 2026) and 21 October 2026 (the model):

- 1. July 2026, awarded day-ahead, USD per kW of the fleet: 0.68 (0.6815)
- 2. January to July 2026, the months held whole: awarded 6.53 (6.5282), the model 30.14 (30.1379), awards as a share of the model 22 percent (21.66)
- 3. The gap of 23.61 (23.6097) in three parts: never offered 9.70 (9.7041), offered and not awarded 14.53 (14.5278), price -0.62 (-0.6222)
- 4. February to July 2026: day-ahead awards 4.17 (4.1713), real-time deviations at the hub average's price 3.00 (2.9974), together 7.17 (7.1688), the model 18.81 (18.8081)
- 5. Resource-hours with a day-ahead energy award: 7.0 percent (127,958 of 1,833,357)

**The whole replication** (`python replication/battery_awards/replicate.py`): **373 of 373 figures** of the page, 0 named, 0 failed; the file `battery_awards_beside.json` **24 of 24**; with `--awards --sced --hub`, **297 of 297 rows** of the two monthly tables recomputed from ERCOT's disclosure over nine months (a dollar sum inside three cents).

**Rulings** (`docs/reviews/battery-awards-faults-2026-11-16.md` rows 5 to 9; `docs/reviews/battery-awards-read-2026-11-16.md` rows 7 to 10):

44. The page does not say the disclosure is no longer pulled; its newest month stays August 2026. Default: the note says it, the page's words unchanged.
45. Grey notes on the page. Default: left; the new block follows the standard.
46. The model beside the awards is 2 hours on the day-ahead schedule while the battery page opens on 4 hours with foresight. Default: 2 hours and day-ahead stay.
47. "It is not in these tables" sits one screen above the real-time section. Default: unchanged.
48. No figure of the page goes through the checked-number component, so `check-values` checks none. Default: not changed on a machine that cannot build.
49. The lead stops at 0.68 and does not point to the real-time section. Default: the lead's words unchanged.
50. Two durations of one fleet on two pages (about 1.9 hours here, 1.65 on `/storage`). Default: the tip unchanged.
51. The gap's three parts cannot be had for one month. Default: over the months together.
52. No A and B of two settlement points. Default: no input added.

---

## 6. Local impact, the forecast tool (`/impact`)

**You sign:** `docs/methods/forecast.md`, section 12.5 "Sign-off". It accepts sections 2 to 8 as completed by 12.1; the defaults and sources of section 2 and of the left box; the property and sales tax readings of sections 4 and 5, each an upper bound where its hover says so; the cross-checks of sections 9 and 12.3 (construction jobs 0.18 to 4.3 times a study's); and what section 10 says the tool cannot see. It leaves open the rulings of `docs/reviews/forecast-faults-2026-11-13.md` (rows 13 and 21) and of `docs/reviews/impact-faults-2026-11-16.md`. The page is under your own review.

**The five choices that matter most** (the left box is the decisions block, every choice edited in place for A and B; the note's section 2):

| Choice | Default | Source |
|---|---|---|
| Capital cost (USD per kW, 2025 dollars) | EIA's overnight cost for the technology in the state, deflated to 2025; a state with several cities is their plain mean | `site/data/forecast/eia_capex.json` (Appendix A, tables 1-13, 1-16, 1-5, 1-11) and `deflator.json` |
| Local content | 100 percent of JEDI's default shares | as `/impact`'s (`economic_impact.md`, section 1) |
| Operating spending | 100 percent of JEDI's default O&M | JEDI's own; section 9 shows JEDI's PV operating jobs at 3.5 times a 2018 study's |
| Discount rate (real) | 7 percent | OMB Circular A-94 (December 2025 text), section 8.b(1) |
| Sales tax rate | the state's rate plus its population-weighted average local rate, midyear 2026 | `sales_tax.json` (Tax Foundation) |

**Cross-check** (the note's sections 9 and 12.3; `docs/reviews/impact-crosscheck-2026-11-16.json`; no figure adjusted):

| Our figure | Published figure | Source | Ours / theirs | Why |
|---|---|---|---|---|
| Colorado wind, 680 MW: construction jobs 2,605 | 1,618 | NREL, Tegen, Goldberg and Milligan, *JEDI II*, NREL/CP-500-40085, June 2006, Figure 4 | 1.61 | two releases twelve years apart, different local shares |
| The same: operating jobs a year 140 (30.8 plant workers) | 259 (88) | the same | 0.54 (0.35) | the paper's 0.13 plant workers a MW against 0.045 in the 2018 release |
| Colorado gas, 270 MW: operating plant workers 13.7 | 14 | the same | 0.98 | operating lines only |
| Lone Mountain Geothermal, Nevada, 36 MW: construction jobs 259 job-years on site | "an estimated 211 full-time construction jobs" | Nevada Governor's Office of Energy, findings and order, 4 November 2026 | 1.23 | workers against job-years of 2,080 hours |
| The same: property tax after the 55 percent abatement, first year, USD 876,631 | USD 876,653 | Nevada Department of Taxation, property tax fiscal note, 24 August 2026 | 1.00 | the tool's rule for NRS 701A.370 |
| The same: paid after abatement, 20 years, USD 16.2 million | USD 15,034,766 | the same | 1.08 | the tool counts the 20 years from the first construction year (ruling 54) |
| The same: sales and use tax on the build: not held | USD 405,537 in full | the Department's sales tax fiscal impact, 19 August 2026 | none | no taxable share is held for geothermal (ruling 55) |

Section 9 holds the ten NREL documents (construction 0.51 to 2.41 for wind).

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\impact"
log using "impact_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(Before it, once, from the repository's root: `python replication/impact/replicate.py --in-dir warehouse/output --rows`, which writes `rows/jedi_tx_wind.csv`, the 24 rows of `nlr_jedi_multipliers` for land-based wind in Texas, with NLR's notice in `rows/NOTICE.txt`.)

**Expected** (16 November 2026; the default project, 200 MW of land-based wind in Texas from 2027):

- 1. construction jobs, job-years: 515.1 (the page: 515)
- 2. operating jobs, each year: 44.74 (the page: 44.7)
- 3. construction earnings, USD of 2025: 41,045,772 (the page: USD 41 million)
- 4. taxes, present value, USD of 2025: 19,915,038 (the page: USD 19.9 million)
- 5. earnings, present value, USD of 2025: 83,592,616 (the page: USD 83.6 million)

**The whole replication** (`python replication/impact/replicate.py`): **7,593 of 7,593 inside the tolerance** over 17 addresses (the default, ten real planned projects of EIA-860M in eight states, six addresses of the value checker); 414 of 414 compared rows of `forecast_tool_parameters` equal the parameter files. Said by its writer: it had read the page's library first, so it is not blind.

**Rulings** (`docs/reviews/impact-faults-2026-11-16.md` rows 5 to 10 and 12; `docs/reviews/impact-read-2026-11-16.md` rows 2 to 12; the progress file, B6):

53. "Taxes, present value" adds only the taxes that have a figure; a zero made of taxes not held reads as "no taxes". Default: unchanged.
54. Nevada's 20 abated years are counted from the first construction year; the Department counts from the first operating year (USD 16.2 million against 15,034,766). Default: unchanged.
55. No taxable share is held for geothermal; Nevada's two notes for one plant disagree (3.3 against 48 percent). Default: stays "not given".
56. New Mexico's ad valorem tax by district adds nothing to a gas plant's severance. Default: unchanged; the note says so.
57. A statute's other tax (Wyoming's wind excise) stands alone on the property tax rows. Default: unchanged; the hover carries the rule's words.
58. Louisiana's gas severance is computed from a rate of a held table. Default: unchanged, as `/severance` draws the same rate.
59. Each field's default is printed under it in grey. Default: unchanged.
60. The jobs in A and B are the three effects added, not workers on site (605 against Nevada's 211). Default: unchanged.
61. No tax figure says who receives it. Default: unchanged.
62. When A and B differ by one input, the table does not say which; no B less A column. Default: unchanged.
63. "Copy A to B" with a new state takes every default of that state. Default: unchanged.
64. "Not held" and "none" stand in each other's place in "Taxes by year". Default: unchanged.
65. Nevada with no rate typed reads "no rule held" where what is missing is a rate. Default: unchanged.
66. A county's own rate typed is carried to all 51 states in "other states". Default: unchanged.
67. "Sales and use tax" is before any exemption and the row does not say so. Default: unchanged.
68. Iowa wind's local tax is typed in two units. Default: unchanged.
69. A wind plant costs USD 1,482 per kW over 25 years here and USD 2,100 over 30 on `/cost-of-power/seller`. Default: each page keeps its source.
70. A figure below a million is written to the dollar beside one in tenths of a million. Default: unchanged.
71. **The one change to the page:** with Nevada's abatement on and a rate typed, "Taxable value" showed 45 percent of the value in abated years; NRS 701A.370 abates 55 percent of the taxes, not of the value, so the column now shows the whole value. No tax, total or present value changed. Default: the change stands; undo is commit `3baff8839`.

---

## 7. The ERCOT peak premium explorer (`/explore/ercot-peak-premium`)

**You sign:** `docs/methods/ercot_peak_premium.md`. It has **no sign-off block**; a signature would go after its section 8 of "The tool as a reader meets it", "Rulings asked", accepting the metrics, the eleven decisions (section 5), the cross-check (section 6) and the replication (section 7).

**The five choices that matter most** (`site/app/explore/ercot-peak-premium/Decisions.tsx`; the note's section 5; none editable, the filters are the choices):

| Choice | Default | Source |
|---|---|---|
| `blocks`: three blocks by the local hour an interval starts | Overnight 21:00 to 12:00, midday 12:00 to 16:00, peak 16:00 to 21:00, every day of the year | the thesis; "Time-of-day blocks" |
| `premium`: the peak median less the midday median, and the peak block's IQR | medians and quartiles, never a mean | "Metrics" |
| `price`: ERCOT's real-time settlement point price, every 15 minutes, each interval counted once | real time, time-weighted; not day-ahead, not load-weighted | NP6-785-ER, NP6-905-CD |
| `no-cap`: every interval is used | no cap, floor or exclusion; February 2021 is in 2021 | "Notation" and "Completeness" |
| `thresholds`: scarcity at or above 1,000 USD/MWh; negative at or below 0; the multiple is P99.9 over the median | 1,000 and 0 | "Metrics"; the thesis's thresholds |

**Cross-check** (the note's section 6; "ours, plain mean" is printed by `from_hourly.py --means` and is not a figure of the page; no figure adjusted):

| Our figure | Published figure | Source | Difference | Why |
|---|---|---|---|---|
| Real-time price, 2024: plain mean 26.83 (median 19.60) | 31.91, ERCOT-wide, load-weighted | Potomac Economics, *2024 State of the Market Report for the ERCOT Electricity Markets*, May 2025, Table 1, page 5 | 5.08 lower (16 percent) | load-weighting; load zones against the four hubs |
| The same, 2023: 48.36 (median 21.37) | 65.13 | the same | 16.77 lower (26 percent) | the same |
| The same, 2022: 62.30 (median 44.02) | 74.92 | the same | 12.62 lower (17 percent) | the same |
| The same, 2021: 148.19 (median 24.60) | 167.88 | the same | 19.69 lower (12 percent) | the same |
| The same, 2020: 21.18 (median 16.56) | 25.73 | the same | 4.55 lower (18 percent) | the same; the five years rank the same in both |
| Prices at or below zero, 2025: 959 intervals, 239.75 hours | "hundreds of hours" | Potomac Economics, *2025 State of the Market Report*, May 2026, page 4 | none | theirs gives no count |
| The highest price, 2022 to 2024: 5,101.55, 5,075.46, 4,981.33 USD/MWh | the offer cap is 5,000 USD per MWh | the 2024 report, page 83 | within 2.1 percent of the cap | not established here |
| The peak-block IQR, the peak less midday, the quartiles, P99.9, the multiple, scarcity counts, every monthly figure | nothing published | | | the page's own measures |

Not read: Table 1 of the 2025 report (its font is not decoded on this machine), so 2025 has no average beside it.

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\ercot_peak_premium"
log using "ercot_peak_premium_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(It reads `ercot_peak_premium_annual` as CSV from its line `global tables`, by default `../../warehouse/output`; part B reads the 15-minute prices.)

**Expected**, on `ercot_peak_premium_annual` as built on 29 September 2026 (2,016 rows); HB_HUBAVG, the whole year, 2015 against 2025:

- 1. peak-block IQR, USD/MWh: 34.12 in 2025 (7.64 in 2015)
- 2. peak median minus midday median, USD/MWh: 14.52 in 2025 (-0.16 in 2015)
- 3. median of all intervals, USD/MWh: 25.68 in 2025 (20.49 in 2015)
- 4. 99.9th percentile, USD/MWh, and the worst-interval multiple: 311.80 and 12.14 in 2025 (583.96 and 28.50 in 2015)
- 5. intervals at or above 1,000 USD/MWh, and at or below 0: 9 and 959 in 2025 (5 and 297 in 2015)

Both years are complete, so these do not move unless ERCOT restates a price.

**The whole replication** (`python replication/ercot_peak_premium/replicate.py`; `from_hourly.py`): **674 of 674 views, 24,786 of 24,786 figures**, 6,214 of 6,214 figures of the two-hub section in 122 views, 12,172 of 12,172 periods written as the note says; **25,704 of 25,704 rows** of the two tables recomputed from the 15-minute prices of all six hubs.

**Rulings** (the note's section 8; `docs/reviews/ercot-peak-premium-faults-2026-11-16.md` rows 8 to 11; `docs/reviews/ercot-peak-premium-read-2026-11-16.md` rows 8 and 10 to 14):

72. The one-line definition says "wider than at midday"; no midday IQR is drawn. Default: the sentence stays.
73. Grey notes drawn by shared frames. Default: not changed here.
74. The chart writes 19.1 where the table writes 19.10 (the shared chart set's rule). Default: not changed.
75. No mean and no traded on-peak block, so no figure can be checked directly against a published one. Default: not built.
76. The tables were 26 days stale; the cloud's daily run does not compute them. Default: a request to the data machine, no schedule changed.
77. The day and hour of a year's highest interval are in no table. Default: not built.
78. A year and one of its months cannot be set side by side. Default: not built.
79. "The thesis" is never named, and `/thesis` is another tool. Default: the words stay.
80. "Worst-interval multiple" is the 99.9th percentile over the median, not the worst interval. Default: the name stays; the block explains it.
81. The CSV of rows drawn holds the first hub only when a second is chosen. Default: not changed (a shared explore file).
82. `/grid`'s "Day-ahead peak" is another measure under the same word. Default: both stay.

---

## 8. The demand growth explorer (`/explore/demand-growth`)

**You sign:** `docs/methods/demand_growth.md`. It has **no sign-off block**; a signature would go after "For the owner's ruling" at the end of "The tool as a reader meets it (session 7508)", accepting the rule in full, the sixteen decisions, the cross-check and the replication, with section "Read as its reader (session 7517)".

**The five choices that matter most** (`site/app/explore/demand-growth/Decisions.tsx`; the note's "The decisions on the page"; none editable):

| Choice | Default | Source |
|---|---|---|
| `base-year`: growth is measured from 2019 | 2019 | the note's decisions |
| `weather`: weather is not removed | as metered | the same |
| `demand-series`: EIA's adjusted demand of the balancing authority; the Lower 48's demand | EIA-930 | the same |
| `hours-used`: an hour is used when held, above zero, within 25 percent of its neighbours' median and inside the range | 25 percent | the same |
| `peak-hour`: peak demand is the highest used hour, an hour's average | the hourly average | the same |

(The note's table of decisions gives each choice and its default; the source of each is on the page's hover.)

**Cross-check** (the note's "What published figures stand against"; no figure adjusted):

| Our figure | Published figure | Source | Difference | Why |
|---|---|---|---|---|
| Lower 48, average demand, 2019 to 2025: +7.03 percent | +7.05 percent (sales) | EIA, Electric Power Monthly, data for August 2026, table 5.1 | 0.02 points | sales against demand at the grid, another form |
| ERCOT, 2019 to 2025: +27.22 percent | Texas retail sales +24.20 percent | EIA-861M, `eia_retail_sales_monthly` | 3.0 points | ERCOT is not all of Texas; sales leave out losses |
| CAISO, 2019 to 2025: +4.45 percent | California sales -2.96 percent | the same | 7.4 points, opposite signs | the read of session 7517 found the cause: EIA-930's California demand counts the batteries' charging |
| 14 highest hours (records before 2026 and the 2026 peaks of seven grids) | the same at EIA's rounding, 14 of 14 | EIA, *Today in Energy*, 15 October 2026 | none | EIA reads the same form |
| PJM highest hour: 152,315 MW (2019), 160,560 MW (2025) | unrestricted peak 151,302 and 160,709 MW | PJM, *2026 PJM Load Forecast Report*, 14 January 2026, tables F-1 and B-1 | +0.7 percent, -0.1 percent | balancing authority demand against PJM's unrestricted load |
| CAISO highest hour: 43,849 MW (2019), 43,860 MW (2025) | 44,301 and 44,506 MW | CAISO, Peak Load History, January 2026 | -1.0 and -1.5 percent | an hour's average against an instant |
| No forecast held | EIA STEO, PJM, NERC and Grid Strategies forecasts | as the note lists them | none | given for scale only |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\demand_growth"
log using "demand_growth_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(It reads `table_rows.csv` beside it, the rows the page reads, committed on the branch; or the page's own download of `eia930_demand_growth`, set in its line `global table`.)

**Expected**, on `eia930_demand_growth` as built on 6 November 2026 (24,116 rows; the year to date to the end of October 2026):

- 1. ERCOT, average demand, growth 2019 to 2025, percent: 27.22 (2019: 43,797.6 MW; 2025: 55,717.2 MW)
- 2. ERCOT, peak demand (the highest hour), growth 2019 to 2025, percent: 12.16 (2019: 74,533 MW; 2025: 83,597 MW)
- 3. ERCOT, the year so far (January to October 2026) against the same months of 2019, percent: 33.34 (2019: 44,790.7 MW; 2026: 59,723.4 MW)
- 4. Lower 48, average demand, growth 2019 to 2025, percent: 7.03 (2019: 458,599.1 MW; 2025: 490,819.4 MW)
- 5. ERCOT, average demand, growth 2024 to 2025, percent: 5.57 (2024: 52,779.8 MW)

**The whole replication** (`python replication/demand_growth/replicate.py`): **35,943 of 35,943 slots of text on 315 views; 777 of 777 growth figures** recomputed (after part B). `from_hourly.py`: 24,060 of 24,062 rows of the table equal from EIA's workbooks of 3 October (the two are EIA's own revision); 54 rows wait for the workbooks of 5 November on the data machine.

**Rulings** (the note's "For the owner's ruling"; `docs/reviews/demand-growth-faults-2026-11-16.md` rows 9, 12 to 15, 17, 18; `docs/reviews/demand-growth-read-2026-11-16.md` rows 2, 6, 11):

83. A month the newest year holds shows its MW and no growth. Default: left, said in the decisions.
84. California's growth is the batteries' charging (+2.81 percent with it, -3.60 without, June to December 2025). Default: the figure stays, the table's own row; the decisions fold says what is in it.
85. Grey notes drawn by the shared frame. Default: not changed here.
86. No second window beside the first. Default: not built.
87. PJM's Load Forecast Report is printed "For Public Use" while its file properties say "Confidential - PJM Personnel Only". Default: its figures are cited.
88. "ERCOT's 2023 record is 85,508 MW" in the note has no document. Default: left in the note, marked.
89. Demand at the grid runs ahead of retail sales in 2026. Default: stated, no cause established.
90. The year-so-far label says "the year so far" twice. Default: words left.
91. No place for a site's own MW (300 MW is 2.52 percent of ERCOT's six years of growth). Default: no input.
92. A forecast sits under the outcome on the All grids tab (CAISO's 46,844 MW forecast against 49,959 MW metered). Default: nothing drawn here.

---

## 9. The interconnection queue explorer (`/explore/interconnection`)

**You sign:** `docs/methods/interconnection_explorer.md`. It has **no sign-off block**; a signature would go after its section "The cross-check" (before "What the tool does not hold"), accepting the assumptions, the twelve decisions, the replication and the cross-check. NYISO, MISO and ISO-NE are held and not read.

**The five choices that matter most** (`site/app/explore/interconnection/Decisions.tsx`; the note's "Assumptions, each with its default and its source"):

| Choice | Default | Source |
|---|---|---|
| A queue is one pull of the operator's report, not a history | the pull the table was last built from (19 October 2026 for CAISO, ERCOT, SPP and ISO-NE; 26 September 2026 for NYISO and MISO) | the header's "Inputs read" line |
| Status groups | operating: completed; withdrawn: withdrawn (SPP also TERMINATED); waiting: active and suspended. For ERCOT "completed" is a signed interconnection agreement, and the page heads it so | `energy_projects.md`, "What counts"; gridstatus 0.36.0, `ercot.py` |
| Withdrawn share | withdrawn over entered, by count | the same |
| Wait | days from queue date to actual in-service date over 365.25, operating positions with both dates; the median | the same |
| Held | NYISO, MISO, ISO-NE: not read, "license needed" | `docs/licenses.md`, `site/data/license_status.json` |

**Cross-check** (against Lawrence Berkeley National Laboratory and GridTracker, *Queued Up: 2026 Edition*, May 2026, CC BY 4.0, as the warehouse holds it; the note's "The cross-check"; no figure adjusted; no host was asked):

| Our figure | Queued Up 2026 | Difference | Why |
|---|---|---|---|
| CAISO, entered 2000 to 2020: 1,910 requests | 1,910 | 0 | the same requests |
| CAISO, the same: withdrawn share 0.787 | 0.781 | +0.006 | pulls ten months apart |
| CAISO, entered 2021: 361 requests | 361 | 0 | |
| CAISO, entered 2023: 4 requests | 594 | -590 | CAISO's public report does not list them |
| ERCOT, entered 2000 to 2020: 198 requests | 1,553 | -1,355 | ERCOT's report lists no withdrawn position and 136 of 459 that reached operation |
| ERCOT, entered 2022: 115 "operating" | 17 in operation | +98 | the table's group is a signed agreement, not operation |
| ERCOT, entered 2025: 354 requests, 104,175 MW | 387, 106,525 MW | -33, -2,350 MW | |
| SPP, entered 2000 to 2020: withdrawn share 0.722 | 0.721 | +0.001 | |
| SPP, entered 2025: 421 requests | 367 | +54 | not established here |
| The median wait by entry year | nothing published by entry year | | Berkeley Lab publishes by online year |

The operators' own totals, FERC's and the EIA's figures were not read.

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\interconnection"
log using "interconnection_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(Before it, once: `python replication/interconnection/fetch_rows.py --from warehouse/output`, which copies `iso_queue_statistics` into `rows/`; the table is held by grid, so it is not in git.)

**Expected**, on `iso_queue_statistics` as built on 21 October 2026 (1,511 rows; CAISO's, ERCOT's and SPP's queues as pulled on 19 October 2026):

- 1. CAISO, positions entered 2023: 4
- 2. CAISO, positions entered 2023 that reached operation: 0
- 3. CAISO, withdrawn share of the positions entered 2023: 1.00
- 4. ERCOT, MW entered 2025 and MW of them still waiting: 104,174.94 and 83,226.25
- 5. SPP, positions entered 2025 and the withdrawn share: 421 and 0.48

**The whole replication** (`python replication/interconnection/replicate.py`): **730 of 730 figures inside the tolerance; 284 of 284 views; 139 queue-years** whose four statuses make up the positions entered. `--queues` from the project-level tables: NYISO 352 of 352 and MISO 113 of 113 equal; CAISO 304 of 309, ISO-NE 245 of 261, SPP 311 of 342, ERCOT 63 of 134, this machine holding an older pull (a data request).

**Rulings** (`docs/reviews/interconnection-faults-2026-11-16.md` rows 2, 14, 15; `docs/reviews/interconnection-read-2026-11-16.md` row 14; the progress file, B9):

93. The page opens on CAISO's newest complete year, which CAISO's report barely holds (4 positions in 2023). Default: the default stays, with its line.
94. Five grey notes under the charts and tables. Default: left, so the page keeps one manner.
95. "Withdrawn, share" is a fraction of 1 (0.80), not a percent. Default: the fraction; the block says "0.80 is 80 in 100".
96. The withdrawn share is by count in the MW view too (0.71 by count, 0.67 by MW for CAISO 2021). Default: by count; a share by MW would be a new table row.
97. ERCOT's "reached operation" is an agreement signed, not a plant running (all 44 positions of 2025 marked completed have an in-service day still to come). Fixed in words on this page only ("Agreement signed"); the cause is the connector's, so the map's Queues tab and every reader of ERCOT's `status` carry it (data request row 40). Default: the words on this page; the connector waits on the data machine.
