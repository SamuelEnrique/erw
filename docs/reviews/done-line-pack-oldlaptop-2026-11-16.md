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

## The second run: six more tools (sessions 7531 to 7551)

Written from the six tools' branches as pushed on 16 and 17 November 2026 (chain 304's second run, samueloldlaptop; tools 11 to 16 of `docs/state/done_line_claims.md`, moved from portable-laptop to this machine by Samuel's word of 16 November 2026, evening). Same form as the nine sittings above: what you sign, the five choices that matter most, the cross-check in one table, the Stata run with what it should print, the whole replication's count, and the rulings with the default each stands on, numbered on from ruling 97. Every figure is copied from the tool's own files on its branch; none was computed for this section. Where a file does not hold something, it is said in place.

- **Every page is in review**, as above. Nothing here opens a page, lifts a hold or publishes anything.
- **The six branches stand on origin/main, not on a wip base** (the progress file gives origin/main at `64da63865` as the base; session 7531's report gives `dd2dabe11` for the events branch; the old base `wip/7500-done-line` and `wip/7200-large-load` are both on main). Each tool's part A and its read are on the same branch; the read moved the branch's head and the landing row's:

| # | Tool | Branch | Head (part A, then the read) | Landing row |
|---:|---|---|---|---:|
| 11 | `/events` and its nine event pages | `wip/7531-events-b` | `984d91a4b`, then `1ee8233fc` (session 7549) | 29 |
| 12 | `/grid/caiso/alerts` | `wip/7532-caiso-alerts` | `ac362d6f6`, then `79c26b05d` (session 7546) | 30 |
| 13 | `/learn/bill` | `wip/7533-learn-bill` | `09eafa96e`, then `2d5c874f6` (session 7547) | 31 |
| 14 | `/learn/problems` | `wip/7534-learn-problems-b` | `430032463`, then `1f79d1450` (session 7548) | 32 |
| 15 | `/play/battery` | `wip/7535-play-battery` | `544328a5b`, then `0fb8d3d3d` (session 7551) | 33 |
| 16 | `/play/ev` | `wip/7536-play-ev` | `95943ca8e`, then `3c5bbabaf` (session 7550) | 34 |

- **Two branches were renamed** (`-b`) after a squash: their first commits saved license-held rows in this public repository (`wip/7531-events` 487 rows, `wip/7534-learn-problems` 702 rows). The old remote branches were deleted, with no force push; the old commits stay reachable by hash on GitHub until collected. See the note's license section.
- **Before you run Stata:** as above. No do-file of these six has been run: Stata is not on this machine. The expected lines are the do-files' own, which their Python mirrors print.
- **Order of the sitting.** One tool a sitting, in the table's order.

---

## 11. The event pages (`/events` and its nine event pages)

**You sign:** `docs/methods/events.md`. It has **no sign-off block**; a signature would go after its section "The replication and the cross-check (session 7531)" (before "The read of 16 November 2026"), accepting "The tool as a reader meets it" (the ten pages, every figure's table and rule, the assumptions, what the tool does not hold, the license hold as it stands, three dated corrections), the fifteen decisions of "The decisions on the pages", and the cross-check. `docs/methods/event_study.md` gains a dated section (the four windows its table of event days left out). The pages have no input: every figure is fixed when the table is built or the page drawn.

**The five choices that matter most** (`site/app/events/Decisions.tsx`; the note's "Assumptions" names these as the ones that move figures most, and its table "The decisions on the pages"):

| Choice | Default | Source |
|---|---|---|
| Each event a fixed window of local days, both ends included | each event's dates (Uri 2021-02-07 to 24; Elliott 2022-12-19 to 29; the 2023 heat 2023-08-01 to 2023-09-10, and the others in each event's section) | the note's section for each event |
| The baseline: the same weekday 364 and 728 days earlier | Uri the same calendar days of 2019 and 2020; COVID-19 2019 and 2018 (the Lower 48 2019 alone) | the note's "Baseline: weekday-aligned" and "Session 49" |
| Demand served, not wanted | EIA-930 demand (load shed is not in it) | the note's "Demand during load shed is load served" |
| A day only when every interval is held; nothing filled | complete days only | the note's "Complete days only" |
| The estimate: weekday and year effects, the event year the average baseline year; no trend (growth since the baseline years counts as effect) and no weather in the first estimate | `dow_year_mean_v1`; 95 percent normal intervals, HC1, z = 1.96 | `event_study.md`, "Specification" and "Inference" |

**Cross-check** (`docs/reviews/events-crosscheck-2026-11-16.md`, 16 rows; ours is `event_window_daily` as retrieved on 19 October 2026; no figure adjusted; nerc.com not read, its robots file disallows named AI agents, so FERC's copies were read; PJM's own Elliott report could not be read, over the reader's 10 MB limit):

| Ours | Theirs | Publisher | Document | Date | Difference | Why |
|---|---|---|---|---|---|---|
| Uri, ERCOT's highest hour: 69,215 MW, 2021-02-14 | 69,871 MW, "ERCOT's 2021 all-time winter peak load" | FERC | *The February 2021 Cold Weather Outages in Texas and the South Central United States ... Tracking of Responses to Recommendations*, page 2 | December 2022 | -656 MW (-0.9 percent) | EIA-930's hourly demand against ERCOT's peak load; the report gives no hour |
| CAISO, August 2020, peak by day: 08-14 46,024; 08-15 44,528; 08-18 46,643; 08-19 45,501 MW | 46,802; 44,957; 47,120; 46,074 MW, "Actual Peak" | CAISO, CPUC and CEC | *Final Root Cause Analysis, Mid-August 2020 Extreme Heat Wave*, Table 5.1, page 78 | 13 January 2021 | -778 (-1.7 percent); -429 (-1.0); -477 (-1.0); -573 (-1.2) | CAISO's peak is its highest instant; EIA's the hourly mean. Both put the highest day on 18 August |
| CAISO, September 2022, highest hour: 51,104 MW, 2022-09-06 | "a record load of 52,061 MW on Sept. 6" | CAISO | *Summer 2022 Heatwave Discussion*, Market Surveillance Committee, page 4 | 21 November 2022 | -957 MW (-1.8 percent) | instant against hourly mean; same day |
| Elliott, PJM's highest hour: 135,328 MW, 2022-12-23 | 134,189 MW (500 kV losses allocated); 135,296 MW, PJM's figure reported elsewhere | FERC, NERC and Regional Entity staff | *Inquiry into Bulk-Power System Operations During December 2022 Winter Storm Elliott*, Figure 13 and note (c), pages 30 and 31 | October 2023 | +1,139 MW (+0.8 percent); +32 MW (+0.02 percent) | how load is defined; EIA agrees with PJM's own to 32 MW |
| Elliott, SPP's highest hour: 47,026 MW, 2022-12-22, 18:00 Central | 47,157 MW, "a new all-time winter peak load ... during Winter Storm Elliott" | FERC, NERC and Regional Entity staff | the same report, page 25 | October 2023 | -131 MW (-0.3 percent) | the report gives no date or hour (ruling 100) |
| ERCOT, summer 2023: 10 August, 6, 7 and 8 September: 85,432; 82,692; 83,913; 84,185 MW | 85,464 MW (10 August); 82,705 MW (6 September); 83,911 MW (7 September); 84,182 MW (8 September) | ERCOT | *ERCOT Provides New Look at Peak Demand Records*; the release of 6 September 2023 | 14 and 6 September 2023 | -32; -13; +2; +3 MW | ERCOT's records are unofficial until settlement; the page's "September record" fixed (fault 4) |
| January 2025 cold, PJM's highest hour: 144,420 MW, 2025-01-22 | "approximately 143,700 MW between 8 a.m. and 9 a.m." | PJM | Inside Lines, *2025 in Review: Operations Improvements See PJM Through Record Peaks, Growing Demand* | 30 December 2025 | +720 MW (+0.5 percent) | PJM's figure is rounded |
| June 2025 heat, PJM's highest hours: 160,560 MW (23 June), 158,646 MW (24 June) | "approximately 162,400 MW and 161,800 MW" | PJM | the same post | 30 December 2025 | -1,840 MW (-1.1 percent); -3,154 MW (-2.0 percent) | approximate; may carry losses; the two days' order agrees |
| Late January 2026 cold, PJM's mean load 24 January to 2 February: 126,887 MW; highest hour 139,410 MW, 2026-01-29 | "an average load of 125,573 MWh"; "remained under 140 GWh" | Monitoring Analytics (the market monitor) | *Winter Storm Fern*, PJM Market Implementation Committee, page 4 | 8 April 2026 | +1,314 MW (+1.0 percent); the highest hour agrees | metered load against demand served as reported to EIA |
| COVID-19, NYISO weekly demand, weeks of 2020-03-29 to 04-26: -11.2, -12.2, -9.6, -5.1, -10.6 percent | "about 13% lower than temperature-comparable historical demand" | EIA | Today in Energy, *Daily electricity demand in New York falls about 13% after COVID-19 mitigation efforts* | 6 May 2020 | ours 1 to 8 points smaller | EIA's weekdays only, weather matched, 2016 to 2019; ours all days, 2018 and 2019, no weather |
| COVID-19, MISO weekly demand, the same weeks: -11.6, -10.0, -8.0, -8.3, -13.1 percent | "decrease by 9%-13% in March and April" (the central region) | EIA | Today in Energy, *Daily electricity demand impacts from COVID-19 mitigation efforts differ by region* | 7 May 2020 | inside EIA's range in four of five weeks | EIA's region is four census divisions, not MISO's footprint |
| Uri's load shed, Uri's highest price (9,051.55 USD/MWh, 2021-02-17), CAISO 2020's load shed, Elliott's outages and load shed | 20,000 MW in ERCOT; 23,418 MW across three grids; no price; 500 MW twice; 90,500 MW; over 5,400 MW | FERC; CAISO | the same reports | | none stands against | the table holds demand served, not shed or outages; no FERC document read gives a price |

Every peak is within 2.0 percent of the operator's own and on the same day. Nothing published stands against the estimates, the carbon intensity of each day, the hub prices beyond ERCOT's, or the peak hour against the baseline in percent.

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\events"
log using "events_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(Before it, once: `python replication/events/replicate.py --tables <dir> --write`, which writes `window_rows.csv` beside the do-file from the public table `event_window_daily`; the rows of ISO-NE's, MISO's and NYISO's hubs are held and not written. The file is also on the branch, 29,469 rows of 19 October 2026.)

**Expected**, on the table as retrieved on 19 October 2026 (copied from the do-file's header):

- 1. Uri, the highest 15-minute real-time price at ERCOT's hub average, 2021: 9,051.55 USD/MWh on 2021-02-17
- 2. Winter Storm Elliott, PJM's highest hour of demand served, 2022-12-19 to 2022-12-29: 135,328 MW on 2022-12-23
- 3. The summer 2023 heat, ERCOT's highest hour, 2023-08-01 to 2023-09-10: 85,432 MW on 2023-08-10
- 4. Uri, the pooled effect on ERCOT's daily demand served: 155,794.96 MWh a day, 95 percent interval 53,420.68 to 258,169.25 (robust, HC1, normal), 54 days
- 5. Elliott, the pooled effect on PJM's daily demand served: 386,999.95 MWh a day, 95 percent interval 256,963.62 to 517,036.28, 33 days

(Stata's own interval uses the t distribution; the do-file computes the pages' normal interval as b plus or minus 1.959964 se.)

**The whole replication** (`python replication/events/replicate.py`): **1,151 of 1,151** after the read (1,149 of 1,149 at part A; 1,176 before the held-row fix, which counts the 27 figures and 3 estimates of ISO-NE's, MISO's and NYISO's hubs as held and recomputes or copies none of them); the table's comparison rows from its level rows 2,890 of 2,890; the builder's 62 pooled estimates not held, with their intervals, 186 of 186; 15 of 15 sentences that state a fact of the rows true.

**Rulings, each with its default** (`docs/reviews/events-faults-2026-11-16.md` rows 1, 7 to 10; `docs/reviews/events-read-2026-11-16.md` rows 3, 4, 6, 8 to 11):

98. **The hold draws EIA's figures "license needed" (fault 1).** On the built pages 1,117 of the 1,127 numbers read "license needed": CAISO's, PJM's, ERCOT's, SPP's and the Lower 48's demand, every carbon intensity, every estimate. The hold of 21 October is by grid (ISO-NE, MISO, NYISO), and a key whose entity names no grid the license module knows (`eia930:PJM`) is held as if the whole table were; the module's own comment says such a row is kept, and EIA-930 is EIA's publication. Default: unchanged, no hold lifted. Choices: (a) EIA-930's entities named to their grids (CAISO, PJM, ERCOT, SPP shown; ISO-NE, MISO, NYISO held); (b) EIA-930 rows read as rows of no grid (all shown); (c) as now. The read met it three more ways, settled by the same choice: the hover on an ERCOT, CAISO or PJM figure names ISO-NE, MISO and NYISO's missing permission (read row 8); the charts' points carry the values the sentences hold, 51,104 MW and 135,328 MW (read row 9); the same EIA hour is public on `/demand` and `/grid/caiso` and held on `/events` and `/learn/problems` (read row 10).
99. Decimals in one column: "47,496" beside "413,170.00" (fault 7; the site's checked-number rule prints a whole number without decimals). Default: unchanged. Choice: fixed decimals for each column of the event study block, with check-values taught the same.
100. SPP's Elliott peak: FERC gives 47,157 MW "during Winter Storm Elliott", while the page says the warehouse holds no SPP peak record (fault 8). Default: unchanged (the cross-check records it). Choice: one sentence citing FERC beside EIA's hour.
101. No weather station for the three newest events (January 2025 cold, June 2025 heat, January 2026 cold), so their estimates carry the weather in full; on the others the weather terms took 47 to 81 percent (fault 9). Default: no new NOAA pull. Choice: approve data request row 50.
102. Grey notes under the charts and caveat paragraphs on every page, against the page standard (fault 10). Default: left as they are; moving them into tips changes every page's structure and wants a browser.
103. Uri's price sat at about 8,970 to 9,002 USD/MWh a day and the page names no offer cap (read row 3). Default: no words added. Choice: one sentence on ERCOT's offer cap of February 2021 from the PUCT's or ERCOT's document.
104. The temperature at Sacramento and Los Angeles (read row 4): the words were corrected (it enters the second estimate only). Default: words only. Choice: one sentence of each airport's hottest day (Sacramento 114.08 F on 2022-09-05, Los Angeles 100.94 F on 2022-09-09), after `wip/7532-caiso-alerts` lands, since session 7546 changes that paragraph.
105. ERCOT's 73,976 MW of 2022-12-23 in Elliott is set against no ERCOT figure (read row 6). Default: nothing added. Choice: a cross-check row and a sentence from ERCOT's release of that week, after its robots file and terms are read.
106. Elliott's day table gives each day without temperature only; the weather share, 65.33 percent, is for the 11 days together (read row 11). Default: unchanged. Choice: a second column, each day with temperature, where a station is held.

Data machine: data request row 49 (which build of `event_window_daily` the live set holds), row 50 (the NOAA pull, only on ruling 101). Browser reads rows 76 to 83 (part A) and 256 to 259 (the read).

---

## 12. The Flex Alert scorecard (`/grid/caiso/alerts`)

**You sign:** `docs/methods/caiso_alerts.md` (new, the page as a reader meets it; `flex_alert_scorecard.md` stays the analysis's method and gains one dated line in its section 3). It has **no sign-off block**; a signature would go at its end, after section 8, accepting the views (section 2), the rules a second implementation needs (section 3), what is recomputed (section 4), the cross-check (section 5) and the eleven decisions (section 6). Every table the page reads is public. The page has no input.

**The five choices that matter most** (`site/app/grid/caiso/alerts/Decisions.tsx`; the note's section 6):

| Choice | Default | Source |
|---|---|---|
| Which notices make an alert day | Flex Alert, EEA Watch, EEA 1 to 3, Alert, Warning, Stage 1 to 3, load interruption; the whole area only. 39 days | CAISO, Grid Emergencies History Report; `flex_alert_scorecard.md`, section 3 |
| Which hours are alert hours | the Flex Alert's window, else the emergency's, else the Warning's; 30 minutes covered; 204 hours | the notices' time frames; section 3 |
| The days the model learns from | the non-alert days of May to October, 2018-07-01 to 2025-10-31: 1,276 | sections 2 and 4 |
| The specification | every term ("chosen"): -503.2 MW pooled; "base" gives +861.2 | sections 4 and 6 |
| The hot-day error is shown, not taken off | not netted (-239.3 MW; netted, -742.5) | section 6 |

**Cross-check** (`docs/reviews/caiso-alerts-crosscheck-2026-11-16.md`; no figure adjusted; CAISO's robots file and terms read first):

| Ours | Theirs | Publisher | Document | Date | Difference | Why |
|---|---|---|---|---|---|---|
| Notices by year and kind, 2018 to 2026 (`caiso_grid_emergencies`, read 13 October 2026) | CAISO's summary tables | CAISO | Grid Emergencies History Report (1998 to present), pages 1 and 3 | revision 10/09/2026 | 66 of 71 year-kind counts equal | the five that differ: 2022 EEA 2, 4 against 5 (CAISO's own record pages list 4, ruling 110); transmission emergencies 2018, 2019, 2022 and RMO 2020, kinds the page does not show |
| Alert days by year: 2018 2, 2019 2, 2020 11, 2021 8, 2022 11, 2023 3, 2024 1 | Flex Alert days: 2, 1, 10, 8, 11, 0, 0 | CAISO | the same report | revision 10/09/2026 | +1 (2019), +1 (2020), 0 (2021, different days), 0 (2022), +3 (2023), +1 (2024) | the page counts any of eleven alert kinds; 2020's Flex Alert for 1 October is dated 30 September in CAISO's list (data request row 59); 2021-07-12 not scored, 2021-07-29 a Warning only |
| The cut on 2022-09-06, alert hours 16:00 to 21:00: -1,452.00 MW (interval -4,565.31 to 1,494.75) | "declined by more than 2,100 MW" within five minutes of the text alert, against the hour-ahead forecast | U.S. EIA | Today in Energy, *California consumers respond to appeals for electricity conservation during heat wave* | 28 September 2022 | opposite in sign, not the same measure | five minutes against CAISO's hour-ahead forecast, against whole hours against a weather-and-calendar model; 98.78 F is hotter than all but one training day |
| The hour 17:00 to 18:00 Pacific, 2022-09-06: 51,104 MW | 51,426 MW at 4:55 p.m., "an all-time high" | U.S. EIA | the same article | 28 September 2022 | 322 MW under | an hour's mean against its highest five minutes |
| 2020-08-17: the model's highest hour 45,349.58 MW; the cut 460.11 MW | day-ahead peak forecast 49,824 MW against the peak 45,169 MW: 4,655 MW, "largely realized due to the statewide efforts" | CAISO, CPUC and CEC | *Final Root Cause Analysis: Mid-August 2020 Extreme Heat Wave*, Table 5.1, printed page 66 | 13 January 2021 | the model stands 4,474.42 MW under CAISO's day-ahead forecast | a forecast a day ahead with forecast weather, against a model given the weather that came; nine days of that table set side by side (the cross-check's section 5, added by the read) |
| The pooled cut (-503.18 MW), its value (USD -5.47 million over 19 hours), the hot-day error (-239.34 MW over 128 days) | nothing published | | | | none stands against | CAISO and the state publish what programs were dispatched, not an estimate of every alert day |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\caiso_alerts"
log using "caiso_alerts_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(Before it, once: `python replication/caiso_alerts/replicate.py --tables <dir> --figures <page_figures.json> --write`, which writes `public_rows.csv` beside the do-file from `flex_alert_effects`, `flex_alert_model` (without its coefficients) and `caiso_dam_alert_day_hub_prices`. The rows are also on the branch.)

**Expected**, on the tables as retrieved on 2 October 2026 (the scorecard) and 13 October 2026 (the notices), copied from the do-file's header:

- 1. Alert days and alert hours, pooled: 38 days, 204 hours
- 2. The pooled cut: -503.18 MW (-503.1849), -102,649.73 MWh (-102649.7289), -1.20 percent (-1.2012) of predicted demand (negative: demand ran above the model)
- 3. Alert days by year: 2018 2, 2019 2, 2020 11, 2021 8, 2022 11, 2023 3, 2024 1; alert hours by year: 8, 12, 71, 36, 58, 12, 7
- 4. The value at the day-ahead price: USD -5.47 million (-5,469,360.66) over 19 alert hours with both hub prices
- 5. The model's check: 128 held-out hot days, bias -239.34 MW (-239.3376); 34 of the 38 alert days at least as hot as the held-out threshold of 87.01 F (87.008)

**The whole replication** (`python replication/caiso_alerts/replicate.py`): after the read, **1,092 figures, 929 rebuilt, 925 inside half the last shown digit, 4 named, 0 fail, 163 named as panel-only** (part A: 634 figures, 471 rebuilt, 467 agree, the same 4 named). The four: two double roundings (ruling 107), one tie ("Days as hot" 77 where the held-out rows show 78, right by the method), one dating fault (2020-10-01, data request row 59). The 163 need the scorecard's panel (bootstrap intervals, the four other specifications, the error over hours, each day's temperature). The alert days rebuilt from CAISO's notices by the rule: 39, the 38 scored and 2021-07-12.

**Rulings, each with its default** (`docs/reviews/caiso-alerts-faults-2026-11-16.md` rows 6, 8 to 11; `docs/reviews/caiso-alerts-read-2026-11-16.md` rows 9 and 11):

107. Double rounding: two cells one off in the last digit (-0.18 for -0.17497; -16,893.33 for -16,893.3249), because the table stores three decimals and the page rounds again. Default: no change. Choice: the builder writes four or more decimals (a data request).
108. Grey text: 13 `text-muted` and 13 `text-xs` marks, against the standard of hover tips only. Default: no change until a session with a browser can move them.
109. At 390 px the ranked table (eight columns) and the table of models scroll sideways inside their frames. Default: no change; browser read row 86 asks what a phone shows. Choice: four columns at 390 px (day, notices, cut, value), the rest on tap.
110. CAISO's summary counts 5 EEA 2 days in 2022; its record pages list 4. Default: the records (4), as the table has it.
111. One clause takes a view: "the size a statewide conservation call might plausibly have" (fault 11; the read's row 11 met it again). Default: kept. Choice: drop the clause and keep the fact ("an effect smaller than 1,598.6 MW, the model's error on a hot evening, cannot be told from zero"). Since the read, a point two sections below gives the published figures with their baselines.
112. Once a daily on-peak index is held for 2018 to 2022, whether the page values those days at it (read row 9). Default: no; an hour is valued at that hour's day-ahead price or not at all ("no price"). Choice: a second, labelled figure at the daily on-peak index.

Data machine: data request row 59 (the Flex Alert of 1 October 2020 dated 30 September), rows 199 to 201 (the four other specifications by day; a daily on-peak price for 2018 to 2022; five-minute demand). Browser reads rows 86 to 89 (part A) and 226 to 228 (the read).

---

## 13. What is on an electricity bill (`/learn/bill`)

**You sign:** `docs/methods/bill.md`. It has **no sign-off block**; a signature would go after its section "The tool as a reader meets it (session 7533)" and the read's section that follows it ("Read as a household with its own bill", session 7547), accepting the views, the fields and their defaults, the arithmetic line by line, the fourteen choices, the cross-check and the replication. Session 335's note above it is kept as written. The bills read no table but for the wholesale price (`cost_of_power_monthly`); every rate is in `site/data/bill_rules.json` with its tariff passage. **This tool's part A also changed a shared component**, `site/components/Num.tsx` (a `bill|` key is held only by the grid of its wholesale price; a total is never held): see the note's license section.

**The five choices that matter most** (`site/app/learn/bill/Decisions.tsx`, 14 lines; the note's "The choices that move a figure"):

| Choice | Default | Source |
|---|---|---|
| Use in the month (`kwh`) | 600 kWh, for all five bills | an assumption of session 43; EIA's Electric Sales, Revenue, and Average Price 2024, Table 5A, gives 503 kWh in California and 1,096 in Texas; Table 6 about 500 for a PG&E home, 506 for SCE, 365 for SDG&E |
| Share of use from 4 to 9 p.m. (`peak-share`) | 20 percent, for PG&E, SCE and SDG&E | PG&E Electric Schedule E-TOU-C, Sheet 1, its own example of pro-rating; taken for SCE and SDG&E as the same assumption |
| Baseline (`baseline`) | PG&E territory T (San Francisco), 7.5 kWh a day in winter; SCE Region 9, 12.0 kWh a day; SDG&E 0 kWh, so no credit | PG&E E-TOU-C Sheet 5 and Preliminary Statement Part A; SCE Preliminary Statement Part H; SDG&E's allowances by climate zone not found as text (its default bill is that much too high: USD 25.68 at 240 kWh, for one) |
| The Texas energy charge (`texas-energy`) | Oncor USD 0.0907 per kWh; CenterPoint USD 0.0853 per kWh | EIA's Texas residential average for July 2026, 158.8 USD/MWh (`eia_retail_electricity_prices`, read 30 September 2026), less each wires company's delivery charges at 600 kWh |
| The wholesale reference (`wholesale-zone`, `wholesale-month`) | PG&E: CAISO NP15; SCE and SDG&E: SP15; Oncor and CenterPoint: ERCOT's hub average; the latest complete month in the table (since the read, a field lists every month held) | `cost_of_power_monthly` (`docs/methods/cost_of_power.md`), which holds the main hubs, not ERCOT's load zones; on 16 November 2026 it holds 48 hours of October, so September 2026 is used |

**Cross-check** (the note's "The cross-check (16 November 2026)", ten rows; robots files and terms read first; Oncor not read, its robots file did not answer in 60 seconds; SCE's and SDG&E's tariff hosts not tried; no figure adjusted):

| Ours | Theirs | Publisher | Document | Date | Difference | Why |
|---|---|---|---|---|---|---|
| PG&E default bill, all in: 38.27 cents/kWh (229.63 USD, 600 kWh, winter) | 39.62 | EIA | Electric Sales, Revenue, and Average Price 2024, Table 6, PG&E bundled residential | released October 2025 | -1.35 | one winter month on today's rates against 2024's revenue over sales, all seasons, CARE households included |
| SCE default bill: 37.46 | 32.43 | EIA | the same table, SCE | October 2025 | +5.03 | the same; SCE's average home used 506 kWh, not 600 |
| SDG&E default bill: 55.48 | 43.63 | EIA | the same table, SDG&E | October 2025 | +11.85 | mostly the baseline credit: the default allowance is 0 (ruling 114) |
| California default bills: 37.46 to 55.48 | 29.75 | EIA | Electric Power Monthly, Table 5.6.A, California residential, August 2026 | released 23 October 2026 | +7.71 to +25.73 | EIA's state average includes the municipal utilities and the CARE and FERA households |
| PG&E bill at 503 kWh: 193.39 USD | 160.86 | EIA | ESRAP 2024, Table 5A, California average monthly residential bill | October 2025 | +32.53 | the same reasons; at PG&E's own 2024 price 503 kWh is USD 199.29 |
| Oncor and CenterPoint default bills: 15.88 cents/kWh | 15.91 | EIA | EPM Table 5.6.A, Texas residential, August 2026 | 23 October 2026 | -0.03 | by construction: set to EIA's July 2026 average (158.8 USD/MWh); August's is 159.1 |
| Oncor bill at 1,096 kWh: 170.68 USD | 163.72 | EIA | ESRAP 2024, Table 5A, Texas average monthly residential bill | October 2025 | +6.96 | today's rates against 2024's (EIA's 2024 Texas price 14.94 cents) |
| The ERW table: California 297.5, Texas 159.1 USD/MWh, August 2026 | 29.75 and 15.91 cents/kWh | EIA | EPM Table 5.6.A | 23 October 2026 | 0 | the table is EIA's own series |
| PG&E E-TOU-C, the rules file's Sheet 2 totals, baseline credit, Base Services Charge, climate credit | the same figures | PG&E | E-TOU-C as posted: Sheet 2 Advice 7921-E effective June 1, 2026; Sheets 1, 3 to 5 Advice 7846-E | read 16 November 2026 | 0 | unchanged since the read of 30 September |
| CenterPoint TC5 Refund: -0.000278 USD/kWh (6th revision, effective 5/18/2026) | 0.000000 (7th revision, effective 11/13/2026) | CenterPoint | Rider TC5 Refund, tariff as posted | read 16 November 2026 | +0.000278 (USD 0.17 on 600 kWh) | the refund ended three days before the read; the page says its rates are as read on 2026-10-01 (ruling 113) |

No publisher prints a bill for a named home on these five tariffs: the totals are checked by the arithmetic and against averages only.

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\bill"
log using "bill_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(No rows to copy first: the do-file types each rate as `site/data/bill_rules.json` holds it. Its Python mirror is `python replication/bill/replicate.py --headline`.)

**Expected** (the default bills: 600 kWh, 30 days, winter in California, 20 percent of use from 4 to 9 p.m.; copied from the do-file's header, which its mirror printed on 16 November 2026):

- California: a PG&E home on time-of-use rate E-TOU-C, the default bill (USD): 229.63
- California: an SCE home (TOU-D-4-9PM), the default bill (USD): 224.76
- California: an SDG&E home (TOU-DR1), the default bill (USD): 332.91
- Texas: a home in Oncor's area of ERCOT, the default bill (USD): 95.27
- Texas: a home in CenterPoint's area (Houston), the default bill (USD): 95.28

- a sixth line, "shares (percent)": the do-file prints it at September 2026's prices (NP15 44.8469, SP15 38.5194, ...) and gives no expected value in its header; the note gives the five shares as 11.72, 10.28, 6.94, 24.88 and 24.88 percent.

**The whole replication** (`python replication/bill/replicate.py`): after the read, **1,209 of 1,209 figures** inside half the page's last shown digit (669 of 669 over 20 cases at part A; on origin/main the same morning 652 of 669, the 17 being the 15 card figures printed "license needed" and two floating-point kWh lines); the PG&E lines equal Sheet 2's totals in every PG&E case.

**Rulings, each with its default** (`docs/reviews/bill-faults-2026-11-16.md` rows 6 to 15; `docs/reviews/bill-read-2026-11-16.md` rows 6 to 11):

113. Re-reading the tariffs: CenterPoint's TC5 Refund went to 0 on 13 November 2026, so its bill is USD 0.17 low at 600 kWh. Default: the page keeps the rates of its stated read date. Yours: whether the rules file is re-read on a schedule, and whether the Texas default energy charge is derived again when it is.
114. SDG&E's default bill has no baseline credit (55.48 cents against EIA's 43.63). Default: as it is, said on the page and in the fold with a figure.
115. The wholesale share counts metered kWh (losses of about 5 percent left out) and sets both Texas homes against ERCOT's hub average, not their load zone. Default: as it is, said in the fold. (The read asked for the zones: data request row 209.)
116. A month missing one hour is not complete, so the page falls back a month (CAISO's October 2025 had 743 of 744 hours). Default: the rule stays.
117. One figure at two precisions: "11.72 percent" on a card, "12 percent" on the bar. Default: as it is.
118. Grey lines (the "For learning, not a bill" paragraph, the words under each card, each glossary source, each line's words). Default: left, counted.
119. One bill at a time where the standard asks for two side by side. Default: one bill; the cards stand for the comparison of defaults.
120. "Ten terms" holds no demand charge (none of the five tariffs charges a home by demand). Default: unchanged; words are yours.
121. No SDG&E climate credit box (the rules file holds SCE's and PG&E's only). Default: as it is, said in the fold.
122. The Texas energy charges come from EIA's July 2026 average; August's (159.1) would give 0.0910 and 0.0856. Default: July, as labelled.
123. Why the wholesale price moved (NP15 12.52 in April, 44.85 in September 2026) is not on the page (read row 6). Default: no words added. Choice: a link from the month field to `/cost-of-power` at the bill's zone.
124. A January bill was charged January's rates; the page holds the rates as read (read row 7). Default: the tip says so; no earlier tariff sheets. Choice: the rules file keyed by effective date.
125. A bill's meter-read dates span two months; the field takes one calendar month (read row 8). Default: one calendar month. Choice: a price weighted by the days of each month.
126. `/play/ev` gives 33.61 cents for California (EIA's state average, July 2026) beside this page's PG&E 38.27 and case 1's 40.86; neither names the other (read row 9). Default: no change on either page. Choice: the EV game's tip names `/learn/bill`.
127. `/learn/problems/prices-and-your-bill`, b3 and b4: "not the power itself" takes the wholesale energy for the power (read row 10). Default: unchanged (another tool's words; the edition of 15 October is frozen). Choice: "not the wholesale price of the energy".
128. Words a household would not know: NP15, SP15, CAISO, "load-weighted real-time price", CARE or FERA (read row 11). Default: unchanged. Choice: glossary terms for them.

Data machine: data request row 69 (`cost_of_power_monthly` last built 4 October 2026), row 209 (ERCOT's Houston and North load zones in that table). Browser reads rows 96 to 101 (part A) and 236 to 238 (the read).

---

## 14. The problem sets (`/learn/problems`)

**You sign:** `docs/methods/problem_sets.md`. It has **no sign-off block**; a signature would go after its section "The replication and the cross-check" (the last of "The tool as a reader meets it (session 7534)"), accepting every view (the index, a set, the edition's students' and teacher's copies, the CSV), the 31 figure rules of "Every figure, set by set", the fifteen decisions and what the sets do not hold. The sets have no input. Live sets ask of the newest rows; the dated edition of 15 October 2026 is frozen. **This branch was squashed and renamed** (`wip/7534-learn-problems` to `-b`): its first commit saved 702 license-held rows (see the note's license section).

**The five choices that matter most** (`site/app/learn/problems/Decisions.tsx`; the note's "The decisions", 15 keys):

| Choice | Default | Source |
|---|---|---|
| Live sets ask of the newest rows; a dated edition keeps its day's (`live`) | rebuilt at most hourly; the edition of 15 October 2026 | the note; ruling 8a |
| A battery question's day (`battery-day`) | the latest day the daily cycle holds, whatever its hours | `storage_daily_cycle` (no hour count) |
| B2's hubs and month (`public-hubs`) | the public rows' hubs; 95 percent of hours | ruling 4; `site/lib/license.ts` |
| D4 and D5's tax (`tax`) | the base rate on the month's mean spot price, no fee; New Mexico's newest rates | `site/data/severance_rules.json` |
| D1's week (`seven-days`) | the seven latest days held in 45 days | session 7534 |

**Cross-check** (`docs/reviews/problem-sets-crosscheck-2026-11-16.md`, 13 rows; ours as the live sets showed them on 16 November 2026 at 22:51 UTC; no new web request this session: set C's documents are those session 7531 read, robots first; nerc.com not read; no figure adjusted):

| Ours | Theirs | Publisher | Document | Date | Difference | Why |
|---|---|---|---|---|---|---|
| C, worked example: Uri, ERCOT's highest hour: 69,215 MW, 2021-02-14 | 69,871 MW, "ERCOT's 2021 all-time winter peak load" | FERC | *The February 2021 Cold Weather Outages in Texas and the South Central United States, Tracking of Responses to Recommendations*, page 2 | December 2022 | -656 MW (-0.9 percent) | EIA-930's hourly demand against ERCOT's peak load, no hour given |
| C3: Elliott, PJM's highest hour: 135,328 MW, 2022-12-23 | 135,296 MW (PJM's figure, note (c) of Figure 13); 134,189 MW with 500 kV losses allocated | FERC, NERC and Regional Entity staff | *Inquiry into Bulk-Power System Operations During December 2022 Winter Storm Elliott*, pages 30 and 31 | October 2023 | +32 MW (+0.02 percent); +1,139 MW (+0.8 percent) | how load is defined; same day |
| C4: ERCOT's highest hour, summer 2023: 85,432 MW, 2023-08-10 | 85,464 MW, "all-time peak demand record" | ERCOT | *ERCOT Provides New Look at Peak Demand Records* | 14 September 2023 | -32 MW (-0.04 percent) | settled hourly load against EIA-930's hour; same day |
| C2: CAISO, August 2020, the day furthest above normal: 18 August (23.50 percent above the baseline) | 18 August the highest "Actual Peak", 47,120 MW against 46,802 MW on 14 August | CAISO, CPUC and CEC | *Final Root Cause Analysis, Mid-August 2020 Extreme Heat Wave*, Table 5.1, page 78 | 13 January 2021 | same day; no baseline in percent | both put the highest demand after the outage days |
| B4: Oncor's default bill, 600 kWh: 95.27 USD at 158.8 USD/MWh | 158.8 USD/MWh, Texas residential, July 2026; 159.1 in August | EIA | *Electric Power Monthly*, average retail price (`eia_retail_electricity_prices`) | retrieved 5 November 2026 | 0 against July by construction; -0.3 USD/MWh against August | the energy charge is set so the default bill equals EIA's July average |
| B3: PG&E's default bill, 600 kWh: 229.63 USD, 382.7 USD/MWh | 297.5 USD/MWh, California residential, August 2026 (336.1 in July) | EIA | the same table | retrieved 5 November 2026 | +85.2 USD/MWh (+28.6 percent) | EIA's average is every utility and customer, discounts and the climate credit included; a definition, not a fault |
| D5: the Comptroller's certified price, August 2026: 1.36 USD/Mcf (2005 dollars), 100 percent credit | the same price | Texas Comptroller | certified prices as `site/data/severance_rules.json` quotes them (tx_cpa_lp_gas) | as of 2026-08 | 0 | the page reads the file |
| D4: oil tax rates: Texas 4.6 percent, Louisiana 12.5 percent, New Mexico 3.75 + 3.15 + 0.24 percent | the statutes and TRD's table as quoted | Texas; Louisiana; New Mexico TRD | Tex. Tax Code Sec. 202.052(a); La. R.S. 47:633; TRD rate table for 1 April to 31 August 2026 | | 0 for Texas and Louisiana | New Mexico's table for October 2026 not read; the period is said (ruling 129) |
| E4: the battery's annual debt service: 6,783,357 USD | the same formula gives 30.38 million on Lazard's own wind case (Lazard: 30.4 million) | Lazard, as `docs/methods/cost_of_power.md` quotes it | | | -0.02 million (rounding) | the formula reproduces Lazard's own case |
| Uri's highest price (9,051.55 USD/MWh); the wholesale shares (11.72, 24.88 percent); ERCOT's and CAISO's peaks and gas shares of 15 November 2026; ERCOT's ties | none read | | | | none stands against | no price in FERC's documents; the shares are the ERW's own; the operators' daily reports were not read |

**Run it in Stata** (this do-file runs from the repository's root, not its own folder):

```stata
cd "C:\path\to\erw"
log using "replication/problem_sets/problem_sets_stata_2026-11-16.log", text replace
do replication/problem_sets/replicate.do
log close
```

(It reads `replication/problem_sets/live_rows.csv`, the rows the five sets were given by the live set at 2026-11-16T22:51:27Z, on the branch with the held rows dropped. Each figure is asserted against the page within 0.005.)

**Expected**, as the pages showed them (copied from the do-file's header; session 7534 checked the five in Python: 2.08, 47.74, 1.12, 24.88, 73.06):

- 1. Know your grid, question 1: ERCOT's peak over CAISO's on 2026-11-15 (UTC): 2.08 times (54,008 / 25,964 MW)
- 2. Know your grid, question 2: ERCOT's natural gas share of net generation, 2026-11-15: 47.74 percent
- 3. Prices and your bill, question 1: ERCOT hub average shape premium, 2026-09: 1.12 USD/MWh (39.50 - 38.39)
- 4. Prices and your bill, question 4: the wholesale share of Oncor's 600 kWh bill: 24.88 percent (bill 95.27 USD)
- 5. Storage and taxes, question 1: ERCOT's batteries out over in, 2026-11-03 to 11-14: 73.06 percent

(The question numbers are the do-file's; since the read, the live page asks the questions in another order and each question says its number in the other copy.)

**The whole replication** (`python replication/problem_sets/replicate.py`): **146 of 146** checks on the live sets' kept reads (every figure by check key, every answer in words), and the edition of 15 October from its own downloads **89 of 92**, 3 network figures named (the edition does not keep its network hour). Unchanged by the read (words only, no figure or key moved). 13 figures (47 occurrences) are drawn "license needed" where the page holds them: 7 of set C (ruling 130) and 6 of set B until `wip/7533-learn-bill` lands.

**Rulings, each with its default** (`docs/reviews/problem-sets-faults-2026-11-16.md` rows 4, 7, 9; `docs/reviews/problem-sets-read-2026-11-16.md` rows 7 to 9; session 7534's report, ruling 1):

129. New Mexico's rates after 31 August 2026: a session reads the Taxation and Revenue Department's table and extends `severance_rules.json`, or the page keeps saying which period it uses. Default: kept, the period said ("the rates the rules file states for 2026-04-01 to 2026-08-31 (TRD table) (the newest it holds; 2026-10 is later)").
130. EIA-930's seven figures of set C drawn "license needed" (23 of set 3's 50 figure places), while the edition's teacher's copy draws them (fault 7; read row 7). Default: unchanged, as ruling 98; the instructor uses the edition for set 3. The choices are ruling 98's.
131. An edition's students' download holds the answers of computed figures, and no tie rows for the network questions (fault 9); for a maximum it holds the two rows the answer picks, not the window's rows (read row 8). Default: as now (the edition is frozen). Choice: from the next edition, an answer is left out of the students' download and its inputs written instead (every row of the window for a maximum).
132. The index names five sets by title, not number; an instructor's "problem set 3" is "When the grid broke" only by order (read row 9). Default: no number added. Choice: "Set 1" to "Set 5".
133. The held rows in the branch's history (commit `710c68ce5`, 702 rows). Session 7534's default was not to rewrite; the branch was since squashed and renamed (`-b`) and the old remote branch deleted, with no force push. What remains for you is in the note's license section (b).

Data machine: data request rows 79 (ERCOT's battery day of 2026-11-14 is a part day: 3,755 MWh out, 24,833 in) and 80 (no ERCOT day of 4 to 8 November). Browser reads rows 106 to 110 (part A) and 246 to 249 (the read).

---

## 15. The home battery game (`/play/battery`)

**You sign:** `docs/methods/battery_game.md`, its section "The done line (session 7535, chain 304, 16 November 2026)". It has **no sign-off block**; a signature would go at the end of that section's "The replication, the cross-check and the faults", accepting the views and the rule of every figure, the fifteen decisions (the first five the player's, editable in the game's settings on Normal and Hard), the two corrections and what the game does not hold. The game's prices are real and its rules its own: no published figure stands against a score. **The read (session 7551, head `0fb8d3d3d`):** `docs/reviews/battery-game-read-2026-11-16.md`. The reader is a student, or a new analyst, who plays a named day and then asks what a real battery of that size would have earned, and a teacher who sets the game for a class. Five cases: Uri, 15 February 2021, Normal; the 2023 heat, 10 August 2023, Hard; the CAISO duck day, 24 July 2026, Easy; a teacher sending a class of 30 to Uri's day; the fleet section beside `/storage`, the awards page and the grid page. 15 rows: 5 site fixed with a test (`site/scripts/test-battery-game-read.mjs`, 44 of 44), 1 data machine, 4 browser, 5 rulings. The fixes: Easy's line in detail with the fleet bonus on hover (Uri: USD 195.25 in the market plus the bonus 44.98 of the perfect battery's 240.23; the duck day 4.58 of 12.98, 35 percent); a sentence giving the trades' money per kW beside the battery page's rules, "not the same measure", linked (the game's perfect battery USD 39.05 per kW from trades on Uri's day; the battery page's 2-hour stress day the same date, energy USD -1.22 per kW and total 318.39 with ancillary services); `?day=uri` addresses and the day's link for a class; CAISO's operating fleet beside ERCOT's (17,094.2 MW in 310 units against 18,204.5 MW in 259), both "the latest inventory"; ECRS, Non-Spin and Base Point Deviation on hover. Uri's and the heat day's prices agree with `/events` to the last digit.

**The five choices that matter most** (`site/app/play/battery/Decisions.tsx`; the note's "The decisions block", defaults read from `lib/battery.ts`):

| Choice | Default | Source |
|---|---|---|
| Usable energy, power, round-trip efficiency (`kwh`, `kw`, `rte`; editable) | 13.5 kWh (5 to 30); 5 kW (1 to 11.5); 90 percent, split evenly (75 to 95) | the note's "The battery's settings" |
| Wear per kWh drawn out of the battery, Hard only (`deg`; editable) | USD 0.11 (0 to 0.30) | Lazard LCOS v10.0 |
| The price played (`price`) | the real-time hub price, no retail rate: ERCOT HB_HUBAVG; CAISO SP15 | "What is real and what is not" |
| Hard's spike toward the cap (`spike`) | USD 5,000 on every grid, at 25, 50, 75, 90 percent | ERCOT market notice M-A120721-01 |
| Lights out pays the whole outage at the value of lost load (`voll`) | USD 35,000 per MWh | "Lights out costs money" (the Commission's figure of 29 August 2024, Project No. 55837) |

**Cross-check** (`docs/reviews/battery-game-crosscheck-2026-11-16.md`, 9 rows; robots files and ERCOT's terms read first; Potomac Economics publishes no terms page a search found; no figure adjusted):

| Ours | Theirs | Publisher | Document | Date | Difference | Why |
|---|---|---|---|---|---|---|
| Uri, 2021-02-15, ERCOT's hub average: 95 of 96 intervals below USD 9,000; lowest 1,403.49, highest 9,004.59, mean 6,764.75 | "energy prices cleared at less than $9,000 per MWh and dipped as low as approximately $1,200 per MWh on February 16"; the order to price load shed "late on February 15" | Potomac Economics | *2021 State of the Market Report for the ERCOT Electricity Markets*, pages 11 and 69 | May 2022 | agrees | the highest interval is 4.59 above the cap: a settlement point price carries adders |
| Uri, "the first day of ERCOT's rotating outages": 2021-02-15 | load resources "deployed at 01:09 on February 15, 2021"; "firm load shed at the outset" | Potomac Economics | the same report, pages 66 and 11 | May 2022 | agrees in substance | the report gives no hour for the first rotating outage |
| The summer scarcity day, 2023-08-10: highest interval 3,842.89 USD/MWh at 15:30 Central | the cap reached "mainly on August 17 and September 6"; demand record "85.7 gigawatts (GW) on August 10" | Potomac Economics | *2023 State of the Market Report for the ERCOT Electricity Markets*, pages 168 and 8 | May 2024 | agrees: 10 August was not a cap day | the day was ERCOT's 2023 demand record, which the day line does not say (ruling 135) |
| Hard's cap: USD 5,000, "since 2023" | USD 5,000, "effective date of January 1, 2022" | ERCOT; Potomac Economics | market notice M-A120721-01; 2021 report page 18, 2023 report page 13 | 7 December 2021 | the cap agrees; the date was a year late | fixed on the page, in `lib/battery.ts` and in the note: "since 1 January 2022" |
| Lights out: USD 35,000 per MWh (the Commission's reliability-standard value) | the value of lost load in ERCOT's price formation: USD 5,000 since 1 January 2022 | Potomac Economics | 2023 report page 13; 2021 report page 18 | May 2024 | two different figures, both the Commission's | planning against shortage pricing (ruling 136) |
| ERCOT's real battery fleet: 19,194.60 MW and 266 units (live set, EIA's September 2026 inventory); this machine's copy 18,204.5 MW, 259 units (August 2026) | "more than 17,000 MW and 31,500 MWh by the end of 2025" | Potomac Economics | *2025 State of the Market Report for the ERCOT Electricity Markets*, page ii, as read on 13 November 2026 (session 5073; not read again) | June 2026 | none at the same date | end of 2025, capacity ERCOT approved to operate; EIA-860M held 13,909 MW in December 2025 |
| The two California days, the calm and the negative days, the battery's defaults | not read, or as cited | | | | none stands against | CAISO's OASIS is a data service; the calm and negative claims are about the warehouse's own table and the replication checks them |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\battery_game"
log using "battery_game_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(Before it, once: `python replication/battery_game/replicate.py --write`, which writes `stata_input.csv` beside the do-file: one row an interval of the heat day and the CAISO duck day, from `site/data/battery_levels.json`, with the perfect plan and the plain rule.)

**Expected** (the levels as frozen on 26 September and 1 October 2026; copied from the do-file's header):

- 1. The heat day at a glance: lowest 24.90, average 511.93 (511.9258), highest 3,842.89 USD/MWh
- 2. The heat day, Normal, the default battery: the perfect battery's score USD 60.97 (60.9710)
- 3. The same day and rules: the plain rule's score USD 43.89 (43.8903)
- 4. The perfect battery's fleet of 10,000 homes: USD 609,710.12
- 5. The duck day: the rise from the 12:00 to 15:00 Pacific mean to the 18:00 to 21:00 mean, 408.90 USD/MWh

**The whole replication** (`python replication/battery_game/replicate.py --tables`): at part A **3,304 of 3,304** (3,290 figures of 105 plays on the seven days and four modes read off the page's own components, the day list's 5, 672 frozen prices and 2 claims about the tables; 3,295 of 3,295 where the tables are not beside the checkout). No score or perfect score changed on any day or mode. After the read: **3,549 of 3,549** with the tables (Easy's line in detail read too).

**Rulings, each with its default** (`docs/reviews/battery-game-faults-2026-11-16.md` rows 7, 9, 10; `docs/reviews/battery-game-read-2026-11-16.md` rows 7 to 11):

134. Hard's debrief lists the plan's trades only, so the battery's work in the outage is not named. Default: keep the debrief to trades (the notice and the banner say what the battery does then). Choice: one clause, "then carried the house from 16:00 to 18:00".
135. The heat day's line, "a hot August day with a 3,842.89 USD/MWh interval", does not say 2023-08-10 was ERCOT's all-time demand record of 2023 (85.7 GW, Potomac 2023, page 8). Default: leave the builder's frozen line. Choice: the builder's line names the record with its source (a data request then).
136. Beside the USD 35,000 the page does not say ERCOT's own shortage pricing uses USD 5,000 since 1 January 2022. Default: leave it. Choice: one sentence naming the market's USD 5,000.
137. The link "What happened" to the event pages is drawn on Normal and Hard only, so a student on Easy, the default, never meets the event page (read row 7). Default: Easy unchanged (your ruling 16 of 14 October 2026: Easy first and less on screen). Choice: the one link on Easy's pick screen too.
138. The score counts the sale of the starting charge and values nothing left at the end: on Uri's day the starting 6.75 kWh is worth about USD 45.66 at the day's average price, a fifth of the perfect battery's 240.23 (read row 8). Default: the game rule stands (since session 38; the end table says it). Choice: a score net of the starting charge at the day's first price.
139. The game's battery, 13.5 kWh and 5 kW, is 2.7 hours, between the battery page's 2 and 4 (read row 9). Default: the battery unchanged; the new sentence names the battery page's 2, 4 or 8 hours.
140. Grey text on the mode line, the day's reason line, the leaderboard's note, the fleet call's source line and the foot (read row 10). Default: unchanged (a restyle of the game is yours to rule). Choice: each grey line made a hover or set in the page's ink.
141. `/events/uri-2021`, `/events/ercot-heat-2023`, `/storage` and `/cost-of-power/battery` do not link to the game (read row 11). Default: no other machine's page changed; a link can now open the day (`/play/battery?day=uri`, `?day=heat`).

Data machine: data request row 89 (the solar day's line names no end of its window), row 239 (each famous day's operating storage MW and MWh at its month, from EIA-860M, into `site/data/battery_levels.json`). Browser reads rows 116 to 119 (part A) and 266 to 269 (the read).

---

## 16. Should your family get an EV? (`/play/ev`)

**You sign:** `docs/methods/ev_game.md`, its section "The game at the done line (session 7536, chain 304, 16 November 2026)" and the read's section after it (session 7550). It has **no sign-off block**; a signature would go after "The cross-check (read 16 November 2026; robots files read first)", accepting which earlier section holds where they disagree (the five screens and "no check key" lines are superseded), every view and figure with its rule, the chart's axes, the eleven choices and what the game does not hold. Nothing the player types leaves the browser. The game's four keys (`ev|...`) name no table, so no figure is drawn "license needed".

**The five choices that matter most** (`site/app/play/ev/Decisions.tsx`; the note's "The choices that move a figure", 11 keys; every one a player can change is changed in the slider the line names):

| Choice | Default | Source |
|---|---|---|
| The home price (`home-price`) | the state's residential average, every utility and hour, not an EV rate (US 18.31 cents, July 2026) | `eia_retail_electricity_prices`, as `site/data/ev_prices.json` holds it (built 15 October 2026) |
| The gasoline price (`gasoline-price`) | regular, the state's weekly series or its PADD region's (US USD 4.354, week of October 5, 2026) | `eia_regional_retail_fuel_prices` (EIA's weekly survey) |
| Both prices held flat for every year (`prices-held`) | flat | the note's "The model" |
| The cars and their prices (`cars`, `car-prices`) | the 2025 Equinox pair at 27 mpg and 0.31 kWh a mile, wall to wheels; before destination, USD 28,600 and 33,600, "to confirm" | fueleconomy.gov and the starting prices as read on 15 October 2026 |
| Net present value (`npv`) and the credit (`credit`) | 5 percent, end of each year, 8 years; the credit off (USD 7,500 when on) | the note's "The model"; the IRS's credit page (no credit after 30 September 2025) |

**Cross-check** (the note's "The cross-check (read 16 November 2026; robots files read first)"; not read: fueleconomy.gov, whose robots file twice refused the connection; PG&E's EV2-A, no PDF reader; Chevrolet's prices):

| Ours | Theirs | Publisher | Document | Date | Difference | Why |
|---|---|---|---|---|---|---|
| US regular gasoline, week of October 5, 2026: USD 4.354 | USD 4.354 | EIA | Weekly U.S. Regular All Formulations Retail Gasoline Prices (EMM_EPMR_PTE_NUS_DPG) | week of 5 October 2026 | 0 | the same survey |
| US regular gasoline, the game's newest: USD 4.354 | USD 3.995 | EIA | the same series | 9 November 2026 | +USD 0.359 | the game's file was built 15 October and not since (data request row 99) |
| US regular gasoline, 1 to 15 July 2026: USD 3.816 (the table's weeks of July 6 and 13) | USD 3.84 | DOE Alternative Fuels Data Center | Alternative Fuel Price Report | July 2026 | -USD 0.024 | AFDC's own survey over the fortnight |
| Residential electricity, August 2026, 13 places: the table US 18.16, CA 29.75, TX 15.91, OH 19.38, NY 28.65, MA 30.48, HI 47.18, FL 14.99, WA 14.63, AL 16.33, LA 12.87, ND 13.31, CT 24.51 cents | the same, each | EIA | Electric Power Monthly, Table 5.6.A | released 23 October 2026 | 0.00 each | the table is EIA's; the game still shows July |
| California's home price: 33.61 cents (July 2026); a year of charging USD 1,563 | PG&E E-TOU-C off-peak total rates, 36.757 cents winter and 39.940 summer: USD 1,709 and 1,857 | PG&E | E-TOU-C as read 30 September 2026 (`site/data/bill_rules.json`) | 30 September 2026 | -3.15 and -6.33 cents | the state's average spreads every utility, hour and baseline credit |
| The federal credit: off; USD 7,500 when on | "not available for vehicles acquired after Sept. 30, 2025"; "up to $7,500" | IRS | Credits for new clean vehicles purchased in 2023 or after | last reviewed 13 July 2026 | none | |

**Run it in Stata:**

```stata
cd "C:\path\to\erw\replication\ev_game"
log using "ev_game_stata_2026-11-16.log", text replace
do replicate.do
log close
```

(No rows to copy first: the do-file types the two prices the game's file holds, `eia:retail_price:US:RES` 2026-07-01 183.1 USD/MWh and `eia:EMM_EPMR_PTE_NUS_DPG` 2026-10-05 USD 4.354 a gallon, and the defaults. Its Python mirror is `python replication/ev_game/replicate.py --headline`.)

**Expected** (the page as every visitor opens it: the United States, every default, the credit off; copied from the do-file's header):

- 1. a year of gasoline (USD): 2418.89
- 2. a year of electricity (USD): 851.41
- 3. saved a year with the EV (USD): 1567.47
- 4. payback (years): 3.1898
- 5. net present value, 8 years at 5 percent (USD): 5130.92

(The page shows them as USD 2,419, 851, 1,567, 3.2 years and 5,131. The read's case 4 worked the electricity by hand to USD 851.42; the do-file's line is 851.41.)

**The whole replication** (`python replication/ev_game/replicate.py`): after the read, **5,245 of 5,245** figures (5,141 of 5,141 over 63 cases at part A: the game as it opens, the 51 states at the defaults, 11 players' cases, every outcome included); the prices of `site/data/ev_prices.json` against the two EIA tables **102 of 104 equal, 2 named** (EIA revised New York's July 2026 residential price from 299.0 to 298.9 USD/MWh and Pennsylvania's from 217.2 to 217.1 after the file was built). No figure the game shows changed in the read.

**Rulings, each with its default** (`docs/reviews/ev-game-faults-2026-11-16.md` rows 6 to 11; `docs/reviews/ev-game-read-2026-11-16.md` rows 5, 8 to 10):

142. The prices' file is rebuilt only by hand; a month-old gasoline price moves a family's payback (at the US defaults USD 3.995 instead of 4.354 gives 3.7 years instead of 3.2). Default: no schedule added; each rebuild is a data request. Choice: `site/scripts/build-ev-prices.mjs` in the data machine's daily run.
143. The home price is the state's average, not an EV or night rate (PG&E's E-TOU-C off-peak 36.757 and 39.940 cents against California's 33.61). Default: the average stays, the fold says so (corrected by the read: E-TOU-C is not a rate made for EV owners).
144. The car prices are the 2025 models' starting prices, "to confirm"; the 2026 models are on sale. Default: unchanged; the player types a dealer's price.
145. The mpg, kWh a mile and miles a year were not read again (fueleconomy.gov refused the connection twice). Default: they stand as read on 15 October 2026, to be read again when it answers.
146. "Interest rate" on the page, "discount rate" in the note: one input. Default: the page keeps "Interest rate"; the note says both.
147. A payback longer than the years kept (Hawaii at the defaults, 8.2 years against 8; an USD 80,000 EV at 13.5 years) reads like any other. Default: unchanged. Choice: "after the years you keep it" under the figure in that case.
148. Table and entity codes in the tips (`eia:retail_price:AZ:RES`) (read row 5). Default: kept, with plain words before them. Choice: the codes only in the table for the parents.
149. No word on what winter does to 0.31 kWh a mile (read row 8). Default: no words added (no source read). Choice: a line from fueleconomy.gov's page on cold weather when it answers.
150. The electricity slider moves by 0.1 cent, so 39.940 is set as 39.9 (read row 9). Default: the slider stays. Choice: a box to type cents to three decimals.
151. One case at a time; no A and B (read row 10). Default: none added (a layout change to the game's one screen, the owner's ruling of 14 October 2026). Choice: a second results column, "B".

Data machine: data request row 99 (rebuild `site/data/ev_prices.json`, then the figures file), row 249 (PG&E's EV2-A rates into the bill rules file). Browser reads rows 126 to 130 (part A) and 276 to 278 (the read).
