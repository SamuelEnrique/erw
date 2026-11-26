# Every state on one page: the page audited as a hostile expert would

Session 10223, chain 710 part D, 26 November 2026, the old laptop. `/states` ("Every state", platform page of chain 581, in review, in no menu): one state or two side by side, from EIA's monthly and annual figures. Read as a state energy office analyst checking his own state's numbers, and as an AI lab's siting team comparing states, each looking for the figure or sentence that is wrong. In the form of `docs/reviews/severance-model-audit-2026-11-26.md` and `demand-model-audit-2026-11-26.md`; their findings are not repeated (the demand audit's request on EIA's revisions to retail sales, its row 2, holds for this page too).

- Nothing changed on main but this file, its evidence folder (`docs/reviews/states-model-audit-2026-11-26/`) and the session report. No table written, no lock taken, no default moved, no model called, no live service asked, no web read.
- Each finding has its own branch, `wip/audit-states-<n>`. Branches that change only words are for landing (the rows at the foot); a branch whose fix would move a figure carries a test only and is not for landing.

## In short

- **The arithmetic is right.** An independent restatement (standard library, written from the method note and the contract, not from the builder or the page's library) rebuilds the generation and retail parts of all 52 page files from the main copy's tables (the largest twelve-month gap 0.9 MWh in 52 places; every all-sector price within half a cent a MWh) and gives 1,197 of the 1,210 figures the page marks in four views to the digit (203 of the default view, Texas: 200). The 13 others are one in the last digit, each the page rounding a figure the file had already rounded (finding 6).
- **"Net interstate trade (in less out)" has the sign the wrong way round (finding 1, High).** EIA's figure is out less in: read the page's way, 23 of 52 states' profiles fail to balance (median gap 43.9 percent); read EIA's way, 51 balance (median 2.7 percent, EIA's direct use). Virginia's row, -45,197,052 MWh, says it sends out 45 TWh more than it takes in; it takes in 45 TWh more. Fixed in words.
- **"Hydro (with pumped storage)" holds no pumped storage (finding 2).** All 22,224 MW of EIA-860M's pumped storage is in "Batteries and pumped storage"; Virginia's hydro line reads 823 MW beside Bath County in storage. In generation, pumped storage sits in "Oil and other" (EIA's code HPS), the line that is below zero in 132 state-years, and the page never says so; nor that rooftop solar is not in EIA's state figures (finding 3). Fixed in words.
- **A source missing months is summed as "the twelve months" (finding 4).** In 44 places a source printed for the last twelve months has months EIA withheld; in DC natural gas, the headline's largest source, is 9 months (40.05 percent), its 3 withheld months (20,722 MWh) in "Not itemized by EIA" (49.15 percent if they are gas). Words for landing; the figure for the owner.
- **"Nothing is filled, scaled or estimated" is true of the ERW and silent on EIA (finding 5).** Form EIA-861M's state sales hold EIA's estimates for utilities it does not survey each month (Texas's 2024 monthly sales 2.07 percent above the annual form's, in the method note and not on the page), and the newest months are revised. Fixed in words.
- **Smaller.** "Puerto Rico is in no other table the page reads": its 6,474 MW are in EIA-860M and in the United States' capacity (finding 7, words; the figure for the owner, -0.45 percent). A nonzero figure printed as 0.0, $0.00 bn or 0.0% in 42 places, against the decision "never drawn as zero" (finding 8, words). "Electricity sold to customers" listed among the fuels of total energy, which already hold it (finding 8, words).
- **Right as stated:** sales times price as revenue, said; the twelve months named; whole years only; nominal dollars, said; the CO2 rate EIA's (51 of 52 within 1 percent of tons over the profile's generation); who operates by people, said; ISO-NE, MISO and NYISO reach the page only as names in EIA's county table and EIA's figures, never an operator's held table.
- **What an expert would add:** the price a large load would pay, not an all-sector average (at one sector mix the cheapest-state ranking moves by up to nine places); what is under construction, not all that is planned (32.8 percent of Texas's 92.7 GW); capacity without batteries (Texas -9.4 percent, California -18.4); grid by capacity, not by people (Kentucky's LG&E 74 percent of the people, 41 percent of the capacity); rooftop solar; use per person. Three data requests.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/states/page.tsx` | The page: the state and second-place choosers; four headlines (net generation and largest source over the twelve months, the all-sector price, CO2 from power with its rate); the monthly note and its link to the Grid tool; "Side by side" (two places); "What it runs on" (yearly and monthly charts, the twelve months by source); "How that changed since 2001" (shares at chosen whole years, the share chart); "What its homes, businesses and industry buy and pay" (the sector table, the price and sales charts); "What is built and what is coming" (capacity by source, the ten largest plants, planned by year, retiring by year, retired); "Who operates its grid" (authorities by people, the state profile's supply and disposition); emissions; natural gas and total energy; large-load laws and the severance link; the decisions fold |
| `site/app/states/Decisions.tsx` | The ten decisions, each with its default and source in a tip |
| `site/lib/states.ts` | The files' shape, the readers (a file by a code the index names), months and years to points, `genShare`, `wholeGenYears`, `byYearTable`, `gridRegion`, `lastCo2`, `yearOfMonths`, `lastWholeYear`; the words of sources (`GEN_SOURCES`, `SECTORS`, `TECH_WORDS`, `CO2_WORDS`, `GAS_WORDS`, `SEDS_WORDS`) |
| `site/lib/mixpage.ts` | `FUEL_WORDS` and `FUEL_COLOR`, the generation groups' names, shared with the Grid tool |
| `site/data/states/index.json`, `<st>.json` | The page files: 52 places, built 2026-11-20 19:12 UTC by the data machine; generation and retail to 2026-08, plants EIA-860M of 2026-09, gas to 2026-07, CO2, SEDS and the profile to 2024, population 2025 |
| `warehouse/derived/states_page.py` | The builder (a step of the data machine's daily run): every part from sixteen ERW tables, the twelve-month windows, whole years, shares, revenue as sales times price, the authorities by county population |
| `warehouse/derived/generation_mix.py` (through `state_generation_mix_monthly`) | The generation groups: coal COW, gas NG, nuclear NUC, hydro HYC, wind WND, solar SUN, other renewables GEO and BIO, oil and other PET, OOG, HPS (pumped storage) and OTH; "not itemized" EIA's all-fuels total less the groups; small-scale solar not included (the table's header) |
| `docs/methods/states_page.md`, `docs/state/page_files_states.md` | The method note (inputs, arithmetic, the cross-check against EIA's state profiles, the decisions) and the files' contract |
| `docs/methods/county_population_and_regions.md`, `generation_mix.md` | The county join and the groups, cited by the page's hovers |
| `replication/states/replicate.py` | The replication of 20 November (1,196 of 1,196 on four views; generation equal to the profiles in five states) |
| Tables read here (the main copy's `warehouse/output/`, read only) | `state_generation_mix_monthly` (retrieved 23 October, rows to 2026-08), `eia_retail_sales_monthly` and `eia_retail_electricity_prices` (5 November, to 2026-08), `eia860m_operating_generators`, `_planned_`, `_retired_` (EIA-860M of 2026-09). The CO2, gas, SEDS, profile, county and population tables are not on this machine: their figures are restated from the files' own rows |

## How every number here was computed

- **The page as drawn:** `draw_states.mjs` draws `site/app/states/page.tsx` with the site's own loaders (`site/scripts/tsx-register.mjs`'s two hooks and the severance audit's `brand-stub.mjs` for `components/Brand.tsx`, which imports Next's fonts), every request refused, for four addresses: the default (Texas alone, months from 2015, natural gas, homes), California with West Virginia, the United States, Connecticut with New York. Every marked figure (`data-fig`) with its hover, every "not held" and "none", the visible text.
- **The restatement:** `restate.py`, standard library, written from the method note's "Arithmetic" and the contract: Part 1 rebuilds the generation and retail parts of every place from the tables and, for the places drawn, the plants from EIA-860M's three sheets; Part 2 forms the printed string of every marked figure (half up on the exact decimal) and sets it beside the drawing.
- **The measures:** `measures.py` and `checks.py` on the page files and the tables.
- Copies of every script and printout: `docs/reviews/states-model-audit-2026-11-26/` (written to run from `runs/c10223/` of a worktree).

## The arithmetic re-done

| View | Marked figures | Equal to the restatement | One in the last digit |
|---|---|---|---|
| Default, Texas | 203 | 200 | Homes' price 15.98 (15.99: revenue over sales 159.8509 USD a MWh); solar coming in 2026 9,933 MW (9,932); SPP's share of the people 4.2% (4.1: 4.1456) |
| California with West Virginia | 363 | 360 | California's commercial price 26.99 twice (27.00); biomass 1,097 MW (1,096) |
| United States | 285 | 282 | net summer solar 171,198 (171,197) and biomass 11,054 (11,053); the ninth plant 3,344 (3,343) |
| Connecticut with New York | 359 | 355 | New York's all-sector price 23.29 twice (23.28); other renewables 1.1% (1.0); petroleum net summer 2,204 (2,203) |

| Figure the default view prints (Texas) | The page | Restated from the tables |
|---|---|---|
| Net generation, September 2025 to August 2026 | 618.9 TWh | 618,933,273 MWh |
| Largest source | 47.3% natural gas | 47.30 |
| Average retail price, all sectors, the twelve months | 10.32 cents a kWh | 103.23 USD a MWh |
| CO2 from power, 2024; rate | 211.9 million t; 373.3 kg per MWh | the file's (EIA's); tons over the profile's generation 374.1 |
| The twelve months by source (9 rows and the total) | 66.4 to 0.1 TWh; 10.7% to 0.0% | equal |
| Shares at 2001, 2005, 2010, 2015, 2020, 2025, and the totals | e.g. coal 36.3% to 11.5%; 372.6 to 601.0 TWh | 60 of 60 equal |
| Each sector, sold, paid, price, customers (August 2026) | 172.2 TWh, $27.52 bn, 15.98 cents, 12,977,001 (homes) ... 534.2 TWh, $55.14 bn, 10.32, 14,919,749 (all) | 19 of 20 equal; homes' price 15.99 |
| Capacity by source, EIA-860M of 2026-09; the ten largest plants; coming; going | 207,230 MW, 1,109 plants; W A Parish 4,008 ... | equal but solar coming in 2026 |
| Who operates (people, 2025) | ERCOT 89.8%, SPP 4.2%, MISO 3.2%, El Paso Electric 2.8% | 89.85, 4.15 (4.1456), 3.23, 2.78 |
| The profile, 2022 to 2024 (15 figures); gas used and produced, 2025 (5); total energy, 2024 (9) | as printed | equal (from the files' rows) |

- **Part 1, all 52 places** (`restate.out`): the twelve-month generation equal to 0.9 MWh at most (Georgia; the builder rounds each month to 0.1 MWh before summing), every window the same (September 2025 to August 2026); the all-sector price equal to 0.005 USD a MWh at most (Virginia); the retail window equal to the generation window in every place.
- **The cross-check of the note** (net generation summed equal to EIA's profile in five states; sales 0.0 to 2.07 percent above the annual form) is the replication's and stands.

## One rule changed at a time

| Rule | The page | Changed to | Measured worth |
|---|---|---|---|
| The sign of net interstate trade | "in less out" | out less in (EIA's) | no figure moves; the profile balances in 51 of 52 places instead of 29 (the rest, EIA's direct use, median 2.7 percent of disposition instead of 43.9) |
| A source in the twelve months | summed over the months EIA prints | "not held" unless all twelve are printed | 44 places print such a source; in 27 it is only "Not itemized" (under 1 percent), in 17 another source too. DC natural gas 40.05% becomes not held and the headline's largest source solar 21.83%; Nebraska gas 4.15, Alaska wind 1.32, Utah hydro 1.59 become not held |
| The same, the withheld months' "not itemized" read as the source | 9 months | 12 | DC natural gas 40.05 becomes 49.15 percent |
| Rounding | the file's figure (shares and prices to 0.01, MW to 0.1) rounded again | revenue over sales, MWh over MWh, rounded once | one in the last digit: 13 of 236 twelve-month prices, 13 of 423 shares, 8 of 109 shares of the people, MW by 1 in a few cells |
| The United States' plants | EIA-860M whole, Puerto Rico in | the 50 states and DC | capacity 1,423,491.7 MW becomes 1,417,017.4 (-0.45 percent); generation and sales exclude Puerto Rico already |
| Price across states | the all-sector average (each state's own sector mix) | each state's sector prices at the United States' mix (37.0, 37.3, 25.5 percent) | Texas 10.32 becomes 10.83 cents, Louisiana 9.74 becomes 10.75, West Virginia 11.45 becomes 12.23; ranks of 49 places move by up to 9 (West Virginia 14th cheapest to 23rd, North Carolina 21st to 14th) |
| Who operates | primary authority by county, by people | by the operating capacity each authority's plants hold | Texas ERCOT 89.85 to 88.52 percent; Kentucky LG&E 74.06 to 40.85; New Mexico PNM 86.85 to 42.53 (CAISO 20.09 of capacity); Indiana PJM 10.43 to 29.31; Missouri AECI 5.00 to 20.15 |
| What is coming | every planned generator EIA-860M lists | under construction only | Texas 92,698 MW to 30,432 (32.8 percent); 39,924 MW "planned, regulatory approvals not initiated". United States 290,264 to 97,944 |
| Operating capacity | with batteries and pumped storage | without | Texas 207.2 to 187.8 GW (-9.4 percent); California -18.4; Arizona -15.6; United States -5.5 |
| Dollars | nominal, said | real | not sized: no price index is held here (data request 3) |
| Solar | utility-scale only (EIA's state figures) | with EIA's small-scale estimate | not sized: not held (data request 1) |

## Each claim against the code

| Claim, or question | Where | What the code does | Verdict |
|---|---|---|---|
| Retail price by sector, and its year | the sector table, the headline, the price chart, the side table | EIA-861M's monthly price by state and sector; the twelve months' price is the summed revenue over the summed sales | **Right as stated**: the caption names the months ("September 2025 to August 2026"); the headline says "the last twelve months" and its window equals the table's in all 52 places today |
| Revenue over sales against a tariff | "Average price", "Paid", the revenue decision | sales times EIA's average price, month by month | **Right as stated**: "Revenue is EIA's sales times EIA's average price"; nothing claims a tariff. An expert's own number is the tariff (below). EIA publishes revenue in the same route; the page computes it (data request 2) |
| Generation mix shares and their year | the twelve-month table, the headline, the yearly shares | twelve months and whole years summed; a source with no month held is null; a source with some months held is summed over those | Whole years: **right**. The twelve months: **finding 4**. What the groups hold: **finding 3** |
| "A source can be below zero: pumped storage uses more than it makes" | the yearly chart's hover | pumped storage is in "Oil and other" | **Finding 3**: the hover never names the line |
| "Hydro (with pumped storage)" | the capacity table | the group `hydro` (conventional only) | **Finding 2** |
| A state's grid operator when it spans several | "Who operates its grid" | each county whole for its primary authority, weighted by people; every authority listed with its share and its shared counties | **Right as stated** ("by county population 2025", the basis in the hover); the link goes to the largest authority's region. By capacity the shares differ widely (above) |
| Rankings across states that report differently | the side table; "Texas, the largest generator of the fifty states" | no ranking is printed; two places side by side; Texas's twelve months 618.9 TWh against Florida's 271.4 | Texas: **right**. Connecticut's people: said (no share). The all-sector price compares sector mixes as much as prices (above): not claimed otherwise, an expert's point |
| Per-capita figures and their population year | none | the population serves only the authorities' shares | **No claim**: no figure per person is printed (Texas would be 16.84 MWh a person a year, California 6.20) |
| Months not whole | every twelve-month window, whole years | windows of twelve months, whole years only; gas's newest whole year (2025, months to 2026-07) | **Right**, but a source inside the window: **finding 4** |
| EIA's revisions and estimates | the decision `as-published`, the hovers | the files as built; nothing on revisions | **Finding 5** |
| Nominal against real | decision `nominal` | nominal, said | **Right as stated** |
| Held grids or internal rows reaching a figure | all | sixteen public tables (EIA, the Census Bureau, the ERW's research of public law); ISO-NE, MISO and NYISO appear only as EIA's authority names | **Right**. Texas's large-load law reads as withheld (the research's own status), with the reason |
| The as-of date of each column | captions, headlines | generation and retail to August 2026 named; capacity "EIA-860M of 2026-09"; customers "August 2026"; CO2, profile, total energy 2024; gas 2025; population 2025; "Files built 2026-11-20" | **Right**: each is printed beside its table. The side table names CO2's year, not the twelve months or the edition |
| "Net interstate trade (in less out)" | the profile table; the hover (the file's note: "positive where the state took in more electricity from other states than it sent out") | EIA's figure as published | **Finding 1** |
| "Puerto Rico is in the generation table and in no other table the page reads" | decision `places` | EIA-860M holds Puerto Rico; the United States' plants take EIA-860M whole | **Finding 7** |
| "A figure ... is never drawn as zero; a zero is a zero the source printed" | decision `not-held` | a figure under the last digit shown prints as 0.0, $0.00 bn or 0.0% | **Finding 8** |
| "Nothing is filled, scaled or estimated" | decision `as-published` | true of the ERW's arithmetic | **Finding 5** for EIA's own estimates |
| Total energy by source, with "Electricity sold to customers" among them | the total energy table | SEDS's total, five fuels and electricity sold, each as published | **Finding 8**: the fuels already hold the electricity sold; Texas's five fuels are 14,672.2 trillion Btu against a total of 14,536.9 (the rest is the net flow of electricity out of the state) |
| CO2 per MWh generated | headline note, side table | EIA's rate | **Right**: tons over the profile's net generation within 1 percent in 51 of 52 places (Vermont 1.65, its tons rounded to thousands) |
| "Monthly, not hourly: no public source gives a state's generation by the hour" | the monthly note | the link to the Grid tool at the largest authority's region (`/grid?region=tex`, which the Grid tool reads) | **Right** |

## What an analyst's or a siting team's own number would hold that this does not

| Item | Size | From |
|---|---|---|
| The price a large load pays: an industrial or a large-power tariff with its demand charge, not an all-sector or class average | the class averages already differ by 2.4 times in Texas (homes 15.98, industry 6.65 cents); at one sector mix the cheapest-state ranking moves by up to 9 places | the files |
| What is under construction, not all that is planned | Texas 32.8 percent of 92.7 GW; United States 33.7 percent | EIA-860M of 2026-09 |
| Capacity that generates, apart from batteries | Texas -9.4, California -18.4, Arizona -15.6 percent | the files |
| Grid by where the plants and the load connect, not by people | Kentucky LG&E 74 to 41 percent; New Mexico PNM 87 to 43 | EIA-860M against the county table |
| Rooftop solar in the mix | not sized | data request 1 |
| Use per person and per customer | Texas 16.84 MWh a person a year, California 6.20, Wyoming 29.85 | the files (not printed) |
| Real dollars | not sized | data request 3 |
| EIA's own revenue and the annual form's sales beside the monthly estimate | the note's 0.0 to 2.07 percent | data request 2; the demand audit's row 2 |

## Findings

| # | Severity | Finding | Measured | Branch | Kind |
|---|---|---|---|---|---|
| 1 | High | "Net interstate trade (in less out)": EIA's figure is out less in | balances 51 of 52 profiles read out less in, 29 read in less out; Virginia -45,197,052 MWh, Pennsylvania +84,824,698, California -53,170,113 each read backwards | `wip/audit-states-1` | words, for landing |
| 2 | Medium | "Hydro (with pumped storage)" holds none; pumped storage is in "Batteries and pumped storage" | 22,224 MW in 18 states; Virginia 3,109 MW of its 3,340 MW storage, hydro 823 MW | `wip/audit-states-2` | words, for landing |
| 3 | Medium | The generation hovers never say pumped storage is in "Oil and other", nor that rooftop solar is not in | "Oil and other" below zero in 132 state-years (Virginia 2024 -906,229 MWh; the twelve months -514,829) | `wip/audit-states-3` | words, for landing |
| 4 | Medium | A source missing months is summed and printed as the twelve months' | 44 places; DC natural gas 9 of 12 months, 40.05 percent (49.15 if the withheld months are gas; solar 21.83 the largest if gas is not held) | `wip/audit-states-3` (words); `wip/audit-states-4` (figure) | words, for landing; figure, the owner's |
| 5 | Medium | "Nothing is filled, scaled or estimated": EIA's monthly figures hold EIA's estimates and are revised | Texas's 2024 monthly sales 2.07 percent above the annual form's (the note's cross-check) | `wip/audit-states-5` | words, for landing |
| 6 | Low | The page rounds the file's rounded figures again | one in the last digit: 13 of 236 prices, 13 of 423 shares, 8 of 109 shares of the people | `wip/audit-states-6` | figure, the owner's |
| 7 | Low | "Puerto Rico is in no other table the page reads"; its plants are in EIA-860M and in the United States' capacity | 6,474.3 MW; the nation's capacity -0.45 percent without it | `wip/audit-states-7` (words); `wip/audit-states-9` (figure) | words, for landing; figure, the owner's |
| 8 | Low | Nonzero figures printed as zero against the decision; "Electricity sold to customers" among the fuels | 42 figures in 52 places; Texas transportation 4,677 MWh as "0.0" TWh and "$0.00 bn" | `wip/audit-states-8` | words, for landing |

- One High, four Medium, three Low. Findings 4, 6 and 7 would move a figure if fixed: each has a test on its own branch, not for landing.

### 1. Net interstate trade is out less in (High)

- **Where.** `site/app/states/page.tsx`, the profile table's row "Net interstate trade (in less out)" and its hover, the files' `disposition.note` ("positive where the state took in more electricity from other states than it sent out"), written by `warehouse/derived/states_page.py` `build_disposition`.
- **Why it is wrong.** EIA's State Electricity Profile lists net interstate trade among the disposition (`docs/methods/eia_state_source_disposition_annual.md`: "Disposition: ... estimated_losses, net_interstate_trade, ..."), so it is what left the state net of what came in. Read that way the profile balances: net generation plus international imports less the trade equals the sales, the losses and the exports to within EIA's direct use, in 51 of 52 places (median 2.7 percent of the disposition; Hawaii, trade 0, -1.5). Read the page's way, 23 places fall below zero and the median gap is 43.9 percent. Every sign on the row is backwards for the reader: Virginia, the datacenter state, -45,197,052 MWh in 2024, reads as sending out 45 TWh net; Virginia sold 138.0 TWh in 2024 (full-service and energy-only) and lost 6.4 TWh against 102.7 TWh made, and took in the rest. Pennsylvania (+84.8 TWh) reads as the largest importer; it is the largest exporter.
- **The test.** `tests/test_audit_states_1.py` on `wip/audit-states-1`: from the files, out less in balances (at most one place below -2 percent, at least 20 below it read the other way, median under 5 percent), Virginia's trade below zero with sales above generation (both pass on main); the words (fail on main).
- **The fix on the branch, words only.** The row reads "Net interstate trade (out less in)"; its hover is the page's own sentence ("a line of the disposition: positive where the state sent more electricity to other states than it took in from them, below zero where it took in more") until the files are rebuilt; the builder's note says the same for the next build; the method note gains the paragraph with the balance. No figure moves (203 of 203 drawn equal).

### 2. "Hydro (with pumped storage)" (Medium)

- **Where.** `site/lib/states.ts` `TECH_WORDS.hydro`, drawn in the capacity table and the retired line.
- **Why it is wrong.** EIA-860M's 122 pumped storage generators (22,224 MW in 18 states) are in the group `storage`, drawn as "Batteries and pumped storage"; `hydro` is conventional hydro. A Virginia reader sees "Hydro (with pumped storage) 823 MW" and Bath County's 3,003 MW nowhere he looks for it; California's 3,704 MW of pumped storage sits in its 20,211 MW of "batteries".
- **The test.** `tests/test_audit_states_2.py` on `wip/audit-states-2`: Virginia's storage over 3,000 MW and hydro under 1,000 (passes on main); the words (fail on main).
- **The fix on the branch, words only.** The label reads "Hydro (pumped storage is under batteries)". No figure moves.

### 3. What the generation groups hold (Medium)

- **Where.** `site/app/states/page.tsx`, the yearly chart's hover ("A source can be below zero: pumped storage uses more than it makes."); `FUEL_WORDS` (`site/lib/mixpage.ts`, shared with the Grid tool, not changed); `state_generation_mix_monthly`'s groups.
- **Why it is wrong.** Pumped storage (EIA's HPS) is summed into "Oil and other", the line that falls below zero (132 whole state-years; Virginia 2024 -906,229 MWh, its twelve months -514,829; South Carolina 2008 -992,568). The hover names pumped storage but not the line, so a reader sees oil running backwards. Solar is utility-scale only: small-scale solar is not in EIA's state figures (the table's header says so; the page does not), which sets California's, Arizona's or New Jersey's solar share below what their grids see.
- **The test and the fix.** `tests/test_audit_states_3.py` on `wip/audit-states-3` (with finding 4's words): Virginia's oil and other below zero (passes on main); the words (fail on main). The hover adds "and it is counted in Oil and other (EIA's code HPS), so that line can fall below zero. Solar is EIA's utility-scale solar: small-scale solar, such as rooftop panels, is not in EIA's state figures here."; the method note gains the line.
- **Not sized:** rooftop solar by state is not held (data request 1).

### 4. A source's twelve months can be fewer than twelve (Medium)

- **Where.** `warehouse/derived/states_page.py` `build_generation` (`sums`: a source with any month held is summed over the months held); the twelve-month table, the headline "Largest source ... of the twelve months' generation", the side table.
- **Why it matters.** Where EIA withholds a source for a month, that month's generation falls into "Not itemized by EIA" (EIA's all-fuels total less the groups), so the total stays whole but the source's sum is short. The method note says a source with no month is null and says nothing of a source with some; the page calls every sum "the twelve months". 44 places print such a source; in 17 a named one: the District of Columbia's natural gas, its headline's largest source, is 9 months (April to June 2026 withheld), 40.05 percent; the withheld months' unitemized 20,722 MWh would make it 49.15. Nebraska's gas (2 months withheld, 4.15 percent), Alaska's wind (3, 1.32), Utah's hydro (1, 1.59) likewise.
- **Words (on `wip/audit-states-3`).** The share's hover adds "A source is summed over the months EIA prints for it: in a month EIA withholds a source, its generation is in Not itemized by EIA, so that source's twelve months can hold fewer than twelve."; the method note gives the counts and DC.
- **The figure (`wip/audit-states-4`, `tests/test_audit_states_4.py`, passes on main).** For Samuel's ruling, default "left as it is": print a source "not held" unless all twelve months are held, as a whole year already is. Effect: DC's natural gas 40.05% becomes not held and its headline's largest source solar at 21.83%; Nebraska's gas, Alaska's wind, Utah's hydro and 16 other named sources (20 in 17 places) become not held; so does "Not itemized" wherever it is short of twelve months (most of the 44).

### 5. EIA's own estimates and revisions (Medium)

- **Where.** `site/app/states/Decisions.tsx`, decision `as-published` ("Nothing is filled, scaled or estimated."); the method note's cross-check, which says it and the page does not.
- **Why it matters.** The ERW fills nothing, but Form EIA-861M's state sales hold EIA's estimate for the utilities it does not survey each month; the annual form replaces them, and the newest months are revised. Texas's 2024 months sum to 505,431,317 MWh against the profile's 495,165,178 (+2.07 percent). A state energy office checking its own sales against the page meets the gap with no word of why.
- **The test and the fix.** `tests/test_audit_states_5.py` on `wip/audit-states-5`: the 2.07 percent from the files (passes on main); the words (fail on main). The decision reads "... The ERW fills, scales and estimates nothing. EIA's monthly figures hold EIA's own estimates (Form EIA-861M's sales include its estimate for the utilities it does not survey each month: Texas's 2024 months sum to 2.07 percent more than the annual form's sales), and EIA revises its newest months."; the note's row follows.

### 6. The files' rounded figures rounded again (Low; a figure)

- **Where.** The builder rounds the twelve-month price to 0.01 USD a MWh, the shares to 0.01 percent, MW to 0.1; the page divides and rounds again (`cents`, `pct`, `whole` in `page.tsx`).
- **How much.** Where the file's last digit is a 5, the printed digit can be one off the figure rounded once: Texas's homes 15.98 cents (159.8509, so 15.99), SPP's share of Texas's people 4.2% (4.1456, so 4.1), New York's all-sector 23.29 (23.28). 13 of 236 twelve-month prices, 13 of 423 twelve-month shares, 8 of 109 shares of the people; MW by 1 in a few cells (Texas's solar coming in 2026, 9,933 against 9,932).
- **The test.** `tests/test_audit_states_6.py` on `wip/audit-states-6` (passes on main). Not for landing.
- **For Samuel's ruling, default "left as it is":** the builder keeps one more digit (or the page computes from revenue, sales and populations, which the files hold); each of the 34 cells moves by one in its last digit.

### 7. Puerto Rico (Low)

- **Where.** Decision `places` ("Puerto Rico is in the generation table and in no other table the page reads, so it has no file"), the contract's same line; `build_plants` takes EIA-860M whole for "US".
- **Why it is wrong.** EIA-860M holds Puerto Rico's 6,474.3 MW (and 3 planned rows), so the United States' capacity, plants, planned and retiring tables hold Puerto Rico while its generation and sales, EIA's national totals, do not (the nation's sales equal the 51 places' sum to 0.4 MWh).
- **Words (`wip/audit-states-7`, `tests/test_audit_states_7.py`).** The decision reads "Puerto Rico has no file: of the tables the page reads, only the generation table and EIA-860M hold it. The United States' capacity, plants, planned and retiring generators are EIA-860M's whole, with Puerto Rico's 6,474 MW in them; its generation and sales are EIA's national totals, without Puerto Rico."; the note's row and the contract follow.
- **The figure (`wip/audit-states-9`, `tests/test_audit_states_9.py`, passes on main).** For Samuel's ruling, default "left as it is": the nation's plants without Puerto Rico; capacity 1,423,491.7 MW becomes 1,417,017.4 (-0.45 percent, 1,423.5 GW to 1,417.0 on the side table).

### 8. Two small sentences (Low)

- **A figure printed as zero.** Decision `not-held`: "It is never drawn as zero; a zero is a zero the source printed." 42 figures in the 52 files print as 0.0 TWh, 0.0% or $0.00 bn though the file holds a figure other than zero (Texas's transportation sales, 4,676.6 MWh and USD 181,244). The decision adds "A figure smaller than half the last digit shown prints as 0.0, 0.0% or $0.00 bn: Texas's transportation sales, 4,677 MWh in the twelve months, print as 0.0 TWh."
- **Electricity among the fuels.** The total energy table lists "Electricity sold to customers" with coal, gas, petroleum, nuclear and renewables; SEDS's total already holds the energy that made it (Texas 2024: five fuels 14,672.2 trillion Btu, total 14,536.9, electricity sold 1,724.5). The row reads "Electricity sold to customers (already counted in the total)".
- `tests/test_audit_states_8.py` on `wip/audit-states-8`: the file facts (pass on main); the words (fail on main).

## The decisions block, line by line

1. `as-published`: **finding 5**.
2. `not-held`: right for "not held"; **finding 8** for figures printed as zero.
3. `first-place`: **right** (Texas 618.9 TWh, Florida 271.4).
4. `twelve-months`: right for the windows (all 52 the same); **finding 4** for a source inside one.
5. `revenue`: **right as stated**; EIA's own revenue would replace the product (data request 2).
6. `who-operates`: **right as stated**; by capacity it reads otherwise (above).
7. `monthly`: **right**; the link resolves to the region.
8. `opening-views`: **right**.
9. `nominal`: **right as stated**.
10. `places`: **finding 7**.

## The branches

Each from `origin/main`, pushed. Tests run on each: its own test and every test file that reads a changed file (`tests/test_session8014_states.py`, `test_session9000_states_laws.py`, `test_session5171.py`), all passing; each words test fails on main and passes on its branch; each file test passes on both.

| Branch | Head | Kind | Files changed | Test | Drawn and read |
|---|---|---|---|---|---|
| `wip/audit-states-1` | `17a83d6aa` | words, for landing | `site/app/states/page.tsx`, `warehouse/derived/states_page.py`, `docs/methods/states_page.md` | `tests/test_audit_states_1.py` | pass (default and Virginia: the row label, its hover 15 times, "in less out" gone) |
| `wip/audit-states-2` | `91a47a564` | words, for landing | `site/lib/states.ts` | `tests/test_audit_states_2.py` | pass (Texas and Virginia capacity tables) |
| `wip/audit-states-3` | `50756c93e` | words, for landing | `site/app/states/page.tsx`, `docs/methods/states_page.md` | `tests/test_audit_states_3.py` | pass (the yearly hover; the share hover 9 times for Texas, 5 for DC) |
| `wip/audit-states-4` | `89c7e865c` | figure, not for landing | test only | `tests/test_audit_states_4.py` | not drawn (no words) |
| `wip/audit-states-5` | `597cc56a5` | words, for landing | `site/app/states/Decisions.tsx`, `docs/methods/states_page.md` | `tests/test_audit_states_5.py` | pass (the decision whole) |
| `wip/audit-states-6` | `0a06fe4c7` | figure, not for landing | test only | `tests/test_audit_states_6.py` | not drawn (no words) |
| `wip/audit-states-7` | `c0b1a3922` | words, for landing | `site/app/states/Decisions.tsx`, `docs/methods/states_page.md`, `docs/state/page_files_states.md` | `tests/test_audit_states_7.py` | pass (the decision whole) |
| `wip/audit-states-8` | `767fc08e1` | words, for landing | `site/app/states/Decisions.tsx`, `site/lib/states.ts` | `tests/test_audit_states_8.py` | pass (the decision and the row) |
| `wip/audit-states-9` | `fb52d61e5` | figure, not for landing | test only | `tests/test_audit_states_9.py` | not drawn (no words) |
| `wip/audit-states-words` | `39944b804` | the six words branches merged onto origin/main | all of the above | all six with the three page tests: 45 passed | pass: default, Virginia and DC drawn; every new sentence read; the default view's 203 figures and 9 "not held" unchanged; no em dash |

The six words branches touch the same four files in different places and merge without a conflict.

## Data requests (rows for the data machine)

1. **Small-scale solar by state.** EIA's estimated small-scale solar generation by state, monthly from 2014 to the newest month (EIA's electric-power-operational-data route, fuel type DPV, or the Electric Power Monthly's table 1.1.A), with each state's utility-scale solar beside it: to size, for each state, the solar share of the page's twelve months with rooftop panels in and out.
2. **EIA's own revenue.** Form EIA-861M's revenue (the retail-sales route's `revenue` column, million dollars) by state and sector, monthly from 2001: set the page's sales times price beside EIA's revenue for each state and sector's newest twelve months, and say the largest gap (the decision `revenue` says within the price's rounding).
3. **A price index.** The Bureau of Labor Statistics' consumer price index (all urban consumers, monthly, from 2001): to state each state's residential and industrial twelve-month prices of 2015 and of the newest twelve months in one year's dollars (the page shows nominal dollars and says so).

## What was checked and found right

- The windows: generation and retail end in the same month in all 52 places (August 2026); gas's newest whole year is 2025 (months to July 2026); CO2, SEDS and the profile 2024; each named beside its table.
- Whole years: null when any month is missing, for a source and for the total, as the note says; the Changed table's "not held" reasons name the year.
- Revenue as sales times price, and the twelve months' price as revenue over sales (the restatement from the tables to 0.005 USD a MWh).
- Capacity, the ten largest plants, coming and going from EIA-860M of 2026-09: equal but the one-in-the-last-digit cells.
- The CO2 rate: EIA's, within 1 percent of tons over the profile's generation in 51 of 52 places.
- The licence line, the tables named on every hover, the "not held" reasons, the region link (`/grid?region=tex` resolves).
- ISO-NE, MISO and NYISO: no operator table reaches the page.

## Not covered, or left open

- The charts' points were not restated one by one; they draw the same arrays as the tables (the yearly chart's axis reaches -100 TWh for Texas because 2001's solar is -0.0 percent, a drawing detail).
- The CO2, gas, SEDS, profile, county and population tables are not on this machine: their figures were restated from the files' own rows, not from the tables.
- The side table's hover cites place A's source for place B's figures (both built together, so the vintages agree today).
- No browser, no width of 390 px: the words branches were drawn with the site's own code and read.

## Landing, rulings and data (returned to the chain's main session)

- **For landing (words only):** `wip/audit-states-1` (`17a83d6aa`), `-2` (`91a47a564`), `-3` (`50756c93e`), `-5` (`597cc56a5`), `-7` (`c0b1a3922`), `-8` (`767fc08e1`), or all six merged as `wip/audit-states-words` (`39944b804`). Each drawn and read: pass.
- **For Samuel's ruling, default "left as it is":** finding 4 (`wip/audit-states-4`): a source not held unless all twelve months are held; DC's headline 40.05% natural gas becomes solar 21.83%, 20 named sources in 17 places become not held. Finding 6 (`wip/audit-states-6`): round once; 34 cells move by one in the last digit. Finding 7 (`wip/audit-states-9`): the nation's plants without Puerto Rico; capacity -0.45 percent (1,423.5 to 1,417.0 GW).
- **Data requests:** the three above.
