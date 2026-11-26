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
| A source in the twelve months | summed over the months EIA prints | "not held" unless all twelve are printed | 44 places print such a source; in 37 it is only "Not itemized" (under 1 percent). DC natural gas 40.05% becomes not held and the headline's largest source solar 21.83%; Nebraska gas 4.15, Alaska wind 1.32, Utah hydro 1.59 become not held |
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

(The sections of each finding, the branches' heads and the drawings are below.)
