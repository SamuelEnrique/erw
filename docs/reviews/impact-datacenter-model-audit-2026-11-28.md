# Datacenters on `/impact`: the model audited as a county's fiscal analyst would

Session 11404, 28 November 2026, chain 770 (part B, item 3), the old laptop. Read as a county's fiscal analyst who has an announced datacenter in front of the board and wants to find the page wrong. In the form of `docs/reviews/battery-model-audit-2026-11-20.md` and chain 710's part B (`docs/reviews/datacenter-model-audit-2026-11-26.md`).

- The page: https://erw-flame.vercel.app/impact?tech=datacenter (in review, as every page is). Technology "Datacenter", any state.
- Nothing changed on main but this file and its folder of evidence (`docs/reviews/impact-datacenter-model-audit-2026-11-28/`). No table written, no lock taken, no default moved, no model called.
- Each finding's test is on its own branch, `wip/audit-impact-<n>`, cut from origin/main. The five branches that change only words are also merged in one branch for landing, `wip/audit-impact-words`; the branch whose fix would move a figure carries its test only.

## In short

- **The arithmetic is right.** An independent restatement written from the method note (`docs/methods/forecast.md` 13.1 and 13.2), not from the page's code, gives every figure of 72 runs (every state's defaults, the three projects below, 21 settings that reach every line) from the page's own files: 21,096 numbers equal to 1e-9 and 1,118 printed texts equal to the character. The five medians the defaults rest on come out of the 93 rows with their counts. Each tax line of three announced projects, drawn by seed 11404 and worked by hand from the statute words the rules file quotes, agrees to the dollar. The published replication passes 16,010 of 16,010.
- **The four plant types are unchanged.** Under the code and files before chain 740's first change (`2b958ba16`) and under origin/main, on the same JEDI rows: 1,020 runs, 21,420 figures and 147,280 year cells, 0 differences.
- **The default state's taxes are all a tax its statute exempts (finding 1, High, words).** The datacenter view opens on Texas: USD 2.68 billion of sales tax over the life (present value USD 1.58 billion), every dollar of its taxes, on equipment Texas exempts for a qualifying data center (Tax Code 151.359). The ERW's own ground names that statute, and Tennessee's, as unread; the page said only "none has been read", and the cell read as tax paid. Tennessee ranks 3rd and Texas 8th of 51 in the other-states chart for the same reason.
- **The default campus holds more builders than any document (finding 3, Medium, for Samuel's ruling).** 833.3 construction workers a USD billion times USD 12 billion is 10,000 workers on site in each of two years; the largest of the 45 documents that state a headcount says 8,000 (USD 100 billion), Meta's Hyperion 7,500 at peak (USD 50 billion). At 400 a billion the Virginia default's taxes fall 10.4 percent in present value, its construction jobs 52 percent.
- **On-site-only totals did not say so (finding 2, Medium, words).** In 48 states every jobs, earnings and income figure is on site only, unmarked in its cell; the lead said "JEDI models read for every state". AWS's Mississippi project with Virginia's ratios has 3.39 times the operating jobs and 81 percent more taxes in present value. The total also left out, unsaid, the building's sales tax (+9.8 percent at a 40 percent taxable share in Virginia).
- **The announced documents.** A sample of 12 of 93 rows (seed 20261128): every figure is inside its quote and parses to its value, with its qualifier and measure; the kept bodies are on the data machine (a data request). Five documents state a wage the picker does not take, and the page did not say so (finding 4, Low, words; Beale's own USD 64,000 against the page's 98,701).
- **Smaller.** "Taxes, present value" is the locality's and the state's together, revenue with no cost netted, never said (finding 5, Low, words: 69 percent local, 29 the state's, in the case measured). The method note's decisions 1 and 2 and one cross-check row quote medians the file no longer holds (finding 6, Low, words).
- **Five branches fix words and move no figure (1, 2, 4, 5, 6); one shows a figure for ruling (3); three data requests.** The words branches merge cleanly onto origin/main with one shared hunk resolved (`wip/audit-impact-words`).

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/impact/page.tsx` | The page: the lead and its hover, the server's read of `nlr_jedi_multipliers`, the datacenter's parameters (`dcParams`) and announced list (`dcProjectList`), the source line |
| `site/app/impact/Forecast.tsx` | The left box and the right side for both kinds of project: the A and B table (`LINES` for every project; `DC_FIGURE`, `DC_TIP`, `DC_LINES`, `dcCellOf`, `dcLeftOut` for a datacenter), the year chart and table, the downloads |
| `site/app/impact/Datacenter.tsx` | The datacenter's own parts: its left-box groups and the announced project picker with its hover (`DcGroups`), the year chart and table (`DcYears`), the same datacenter in other states (`DcOtherStates`) |
| `site/app/impact/StateChart.tsx` | The plants' other-states chart (not the datacenter's) |
| `site/lib/dcimpact.ts` | The datacenter model, pure: defaults (`dcDefaults`), wages, Virginia/Georgia/Minnesota ratios (`dcChain`), eligibility (`dcEligible`), the exemption's years, the electricity tax (`dcElecTax`), the run by year with sums and present values (`dcRun`), display, check keys |
| `site/lib/dcui.ts` | The datacenter's fields, ranges and hover words (`DC_FIELDS`, with the source links), the resolve of a scenario's values to inputs (`dcResolve`), the picker's projects (`dcProjects`: MW, investment in 2025 dollars, permanent jobs, construction workers, what is not taken) |
| `site/lib/dcfiles.ts` | The run's CSV, Python and Stata files for a datacenter |
| `site/lib/forecastdata.ts`, `forecastui.ts`, `forecast.ts`, `impact.ts` | The parameter files as the page reads them; the address and scenario state; the plants' model; the technology and state lists |
| `site/data/forecast/datacenter_announced.json` | The 93 announced rows with their documents' words, and the five medians (computed 27 November 2026) |
| `site/data/forecast/datacenter_rules.json` | JLARC's split, refresh, build time; the horizon; the three states' multipliers; 46 states' exemption, property and electricity rules, each with its statute quote and hover |
| `site/data/forecast/datacenter_wages.json`, `sales_tax.json`, `income_tax.json`, `deflator.json` | CBP 2023 payroll per job by state (NAICS 518210; 2362 and 238); Tax Foundation's 2026 rates; the 2026 brackets; the GDP deflator |
| `site/data/forecast/` (the plants' files) | `jedi_costs`, `eia_capex`, `capacity_factors`, `jedi_taxable`, `property_rules`, `sales_exemptions`, `gas`, and since 27 November `coal`, `biopower`, `csp_trough` |
| `warehouse/forecast/datacenter_announced.py`, `datacenter_announced_rows.json` | The builder of the announced file from the transcribed rows (it checks each `says` inside its quote and its parse, and with `--verify-reads` each quote against the kept body on the data machine) |
| `warehouse/forecast/datacenter_rules_check.py`, `datacenter_rules_table.py`, `datacenter_wages.py`, `params.py`, `jedi_costs.py`, `eia_capex.py`, `pdf_strike.py`, `income_official.json` | The rules' quote check and the note's table; the wages; the plants' parameters |
| `docs/methods/forecast.md` sections 13 and 14 | The datacenter's method (internal, never linked from the page): what it computes, defaults, the 46 states, 27 decisions, the cross-check; coal, biopower and the trough |
| `docs/methods/economic_impact.md`, `docs/methods/impact_tax_rules.md` | The plants' JEDI note and the tax rules table's note (the page links no method note: only `/data`) |
| `replication/impact/datacenter/` | `replicate.py` (16,010 of 16,010 here), the do-file, `page_figures.json` |
| `site/scripts/dc-figures.mjs`, `dc-crosscheck.mjs`, `dc-files-check.mjs`, `test-impact-pins.test.mjs`, `test-datacenter.test.mjs`, `test-datacenter-ui.test.mjs` | The replication's figures, the cross-check, the files' check, the 32 plant pins, the model's and the picker's tests |
| `docs/reviews/impact-datacenter-sources-2026-11-26.md`, `impact-datacenter-readers-2026-11-26.md`, `impact-datacenter-crosscheck-2026-11-26.json` | Chain 740's ground (every source with its robots file and verdict), its readers' cases, its cross-check |
| `docs/state/progress_c740.md`, `note_2026-11-26_window3_c740.md`, and `git log origin/main -- warehouse/forecast site/data/forecast site/app/impact` | What chain 740 built and left for Samuel; since then coal, biopower, the CSP trough and the announced rows from 68 to 93 (session 10822) |

## How every number here was computed

- **The page's own code:** `dc_page.mjs` runs `forecastdata.ts`'s `dcParams` and `dcProjectList`, `dcui.ts`'s `dcResolve` and `dcimpact.ts`'s `dcRun`, `dcStat` and `dcDisplay`, as `Forecast.tsx` calls them, for 72 cases: every state's defaults; the three projects as the picker sets them, bare and with a county's figures typed; 15 settings (Ohio's and Illinois' electricity, Louisiana abated in full for 10 years, Georgia from 2030, Minnesota at the state's rate, Maryland's two terms, Florida at 99 MW, South Carolina from 2032, Washington from 2034, Montana below class seventeen, Virginia without the exemption, with the equipment bought once, with the building falling over 40 years).
- **The independent restatement:** `restate.py` (standard library), written from 13.1 and 13.2 and the rules file's words: the medians from the rows, the defaults, the picker's figures, every year's jobs, earnings, purchases, sales tax before, forgone and paid, property, income and electricity tax, sums and present values. `compare.py` and `display.py` set the two side by side.
- **One choice at a time:** `measures.mjs` (the page's model with one input or one parameter changed). **The plants:** `plants.mjs` under each tree (`git archive 2b958ba16` of `site/lib/forecast.ts` and `site/data/forecast/`) and `plants_compare.py`. **The draws:** `sample.py`. **The documents:** `docs12.py`. **The pages drawn to HTML:** `draw.mjs` (the page's own components, no server).
- JEDI rows: `warehouse/output/nlr_jedi_multipliers.csv` of the main checkout (21 October 2026, before coal), read only, the same for both trees.
- Copies of every script and its printout are in the folder of evidence; the scripts run from `runs/c770/s11404/` of a worktree (Python from the root, the `.mjs` from `site/` with `--import ./scripts/tsx-register.mjs`).

## The arithmetic re-done: the default figures the page prints

The datacenter view opens on Texas (the page's default state) at the defaults; Virginia is the state with a study, an exemption and an electricity tax.

| Figure the page prints | Texas, the page | Virginia, the page | Restated | Gap |
|---|---|---|---|---|
| Size, investment (grey defaults) | 1,000 MW; USD 12,000 million | the same | median 1,000 of 17; 12.0 a MW of 13 | 0 |
| Permanent jobs; construction workers a year | 322.5; 10,000 | the same | 0.3225 a MW of 11; 833.333333 a billion of 25 | 0 |
| Earnings per job, operations; construction | USD 130,137; 74,765 | USD 152,609; 74,336 | CBP 2023 times 128.90425 / 122.452 | 0 |
| Sales tax rate | 8.2 | 5.77 | state plus average local | 0 |
| Construction jobs | 20,000 | 33,635 | 10,000 x 2; Virginia x 1.681772 (JLARC D-3) | 0 |
| Operating jobs, each year | 323 | 1,093 | 322.5; x 3.388520 (JLARC D-5) | 0 |
| Construction earnings | USD 1.5 billion | USD 2.41 billion | 1,495,300,000; 2,405,569,809 | 0 |
| Operating earnings, each year | USD 42 million | USD 139.5 million | 41,969,183; 139,458,209 | 0 |
| Sales and use tax (paid) | USD 2.68 billion | USD 944.4 million | 2,684,352,000; 944,433,600 | 0 |
| State income tax over the life | USD 0 | USD 253.5 million | 0; 253,521,665 | 0 |
| Taxes, present value | USD 1.58 billion | USD 537.1 million | 1,577,476,774; 537,056,350 | 0 |
| Earnings, present value | USD 1.86 billion | USD 3.71 billion | 1,861,923,007; 3,707,651,404 | 0 |
| Before the exemption; forgone | USD 2.68 billion; not held | USD 1.89 billion; USD 944.4 million | 1,888,867,200; 944,433,600 | 0 |
| Property, electricity | not held (rates and MWh not given) | not held | null | 0 |

- **72 cases, 21,096 numbers, 0 differences** (to 1e-9 relative); **1,118 printed texts, 0 differences** (half away from zero, as the browser rounds).
- **The defaults note** ("medians over the announced projects ... 93 in the list, as of 2026-11-27 ... 21 of the list are campuses' figures to date, which enter no median"): 93 rows, 21 to date, 72 in the medians, counts 17, 13, 11 and 25: right.
- **The builder reproduces its file.** `warehouse/forecast/datacenter_announced.py`, run here by mistake without arguments, rewrote `site/data/forecast/datacenter_announced.json` in this worktree with content identical to the committed file (line endings only); the file was restored from git (a slip, the report says so).

## Three announced projects, each tax line by hand from its statute

Drawn by `random.Random(11404).sample(k=3)` from the 87 rows whose investment the picker takes: **AWS's Madison County complexes, Mississippi** (`ms_aws_madison_2024`), **Google's Virginia investment** (`va_google_2025`), **Beale Infrastructure's Project Blue, Pima County, Arizona** (`az_beale_pima_2025`). Each as the picker sets it, the rest at the state's defaults (first construction year 2027, two years, 20 operating years, JLARC's split, equipment again every 5 years); the property and electricity lines with a county's figures typed, since no state rate is held. Every figure below equals the page's.

### AWS, Madison County, Mississippi

- **Picked:** USD 10 billion (2024) times 128.90425 / 125.59075 = **USD 10,263.83 million**; 1,000 permanent jobs ("at least 1,000 new jobs"); MW not stated (default 1,000); construction workers not stated: 10.26383 x 833.333333 = **8,553.2** a year.
- **Sales and use tax.** Equipment 68.2 percent: USD 6,999,932,060; half in each build year, 3,499,966,030. Rate 7.00 + 0.06 = 7.06 percent: **USD 247,097,602** before, each build year.
- **The exemption.** The rules file quotes the Mississippi Development Authority's sheet: "Businesses must invest at least $20 million and must create at least 20 new jobs paying 125 percent of the average state wage". USD 10,263.83 million and 1,000 jobs qualify (the wage condition not checked, as the hover says). It covers equipment, new and replacement, and the initial construction, at the state's part of the rate: 7.00 / 7.06 = 0.991501. Forgone each build year USD 244,997,622; paid 2,099,980.
- **The refreshes** (2034, 2039, 2044; no end year in the sheet): 6,999,932,060 x 7.06 percent = 494,195,203 before, 489,995,244 forgone, 4,199,959 paid each.
- **Over the life:** before USD 1,976,780,814; forgone 1,959,980,977; paid **16,799,837** (the local 0.06 percent). The page: USD 16.8 million paid, 1.96 billion forgone.
- **Income tax** (brackets: 4 percent over USD 10,000; deduction 2,300, exemption 6,000). Operations: wage 62,027.14 x 1.052689 = 65,295; taxable 56,995; tax 1,879.80 a job; x 1,000 x 20 years = 37,596,000. Construction: wage 66,508; taxable 58,208; tax 1,928.32; x 8,553.2 x 2 = 32,986,613. **USD 70,582,613** (the page: 70.6 million).
- **Property** (Mississippi DOR: Class II real and Class III personal property "15%"), with a county's 10.5 percent of assessed value typed and a fee in lieu of half the tax for 10 years: building 2,011,710,680 x 0.15 x 0.105 x 0.5 = 15,842,222; equipment 6,999,932,060 x 0.15 x 0.105 x 0.5 = 55,124,465; **USD 70,966,687** in the first operating year, twice that from the eleventh; **USD 2,129,000,597** over 20 years. The page: the same.
- **Not held:** the Code (57-113-21) itself, read from the sheet (decision 24); any project-specific act of the Legislature for this campus is not read.

### Google, Virginia (Chesterfield, Loudoun and Prince William)

- **Picked:** USD 9 billion (2025): **USD 9,000 million**. The document states no jobs and no MW: permanent jobs stay the default 322.5 (1,000 MW x 0.3225), construction workers 9 x 833.333333 = 7,500.
- **Sales and use tax.** Equipment USD 6,138,000,000; 3,069,000,000 a build year; 5.77 percent: **USD 177,081,300** before each build year.
- **The exemption.** Code 58.1-609.3(18) as quoted: "Beginning July 1, 2010, and ending June 30, 2035 ... computer equipment or enabling software purchased or leased for the processing, storage, retrieval, or communication of data ...", for "a new capital investment ... of at least $150 million" and "at least 50 new jobs". USD 9,000 million qualifies; the 50 jobs are met only by the default's 322.5, which come from the default MW, not from the document (and the wage test is not checked). Purchases through 2034 in whole years: the two build years and the 2034 refresh forgo all of their tax; 2039 and 2044 pay **USD 354,162,600** each. Over the life: before 1,416,650,400, forgone 708,325,200, paid **708,325,200**. The page: the same.
- **Income tax.** Operations: 322.5 on site x (1 + 6,615/4,373 + 3,830/4,373) = 1,092.80 jobs; earnings 49,216,403 x (1 + 552.2/419.4 + 216.8/419.4) = 139,458,209; average 127,615; taxable 117,935 (deduction 8,750, exemption 930); tax 720 + 100,935 x 5.75 percent = 6,523.78 a job; **USD 7,129,200** a year. Construction: 7,500 x 1.681772 = 12,613.29 jobs; earnings 557,520,000 x 1.618038 = 902,088,678; average 71,519; tax 3,298.24; **USD 41,601,622** a build year. Over the life **USD 225,787,250**. The page: the same.
- **Property** (58.1-3506(A)(43): "Computer equipment and peripherals used in a data center", a class of its own; fixtures and buildings at 100 percent), with Loudoun County's 2026 rates typed (real estate USD 0.875 per 100, computer equipment 4.15 per 100) and its schedule (60, 15 points, floor 10): building 1,764,000,000 x 0.875 percent = 15,435,000; equipment 6,138,000,000 x 60 percent x 4.15 percent = 152,836,200; **USD 168,271,200** in the first operating year. The page: the same.
- **The building's sales tax**, its taxable share typed at 40 percent: 882,000,000 x 0.4 x 5.77 percent = **USD 20,356,560** a build year, paid (the exemption does not reach "general building improvements").
- **Electricity** (58.1-2900: "... in excess of 50,000 kWh at the rate of $0.000875 per kWh"), 300 MW all year, 2,628,000 MWh: 219,000,000 kWh a month; 2,500 x 0.001595 + 47,500 x 0.001085 + 218,950,000 x 0.000875 = 191,636.78; **USD 2,299,641** a year. The page: the same. The two lower blocks' rates have no quote in the rules file; together they are worth USD 141 a year.

### Beale Infrastructure, Project Blue, Pima County, Arizona

- **Picked:** USD 3.6 billion (2025): **USD 3,600 million**; 180 permanent jobs; 3,000 construction workers in each year (the document: "3,000 or more direct construction jobs ... during construction"); MW not stated (default 1,000).
- **Sales and use tax.** Equipment USD 2,455,200,000; 1,227,600,000 a build year; 5.6 + 2.94 = 8.54 percent: **USD 104,837,040** before each build year; a refresh 209,674,080.
- **The exemption.** A.R.S. 41-1519 as quoted: "$50,000,000 of new investment ... if the computer data center is located in a county with a population of more than eight hundred thousand persons"; 42-5061(B)(23) for the equipment during the qualification period, "expiring at the end of the tenth full calendar year following the calendar year containing the effective date". Pima County has more than 800,000 people, so the USD 50 million threshold is the right one here (the tool uses it in every county). Certified in 2027, the period runs through 2037: the build years and the 2034 refresh forgo their tax, 2039 and 2044 pay. Before 838,696,320; forgone 419,348,160; paid **419,348,160**. The page: the same.
- **Income tax** (2.5 percent flat over the file's standard deduction of USD 8,350): operations: wage 93,761 x 1.052689 = 98,701, tax (98,701 - 8,350) x 2.5 percent = 2,258.78 a job, x 180 x 20 = 8,131,575; construction 73,547, tax 1,629.93 x 3,000 x 2 = 9,779,565; **USD 17,911,140**. The page: the same. The deduction is a data request (below).
- **Property** (42-15001: "17. Fifteen percent beginning from and after December 31, 2026", class one), at a typed 12 percent of assessed value: building 705,600,000 x 0.15 x 0.12 = 12,700,800; equipment 2,455,200,000 x 0.15 x 0.12 = 44,193,600. The page: the same.
- **What the document states and the page does not take:** "$1.2 billion for construction and another $2.4 billion for equipment" (66.7 percent, against JLARC's 68.2) and "average salaries of $64,000" (the page: CBP's 98,701). Finding 4.

## The abatement and exemption arithmetic re-done

- **Abatement:** a share off the tax (not the value) of building and equipment, from the first operating year for the typed years. Re-done for Mississippi (50 percent, 10 years), Louisiana (100 percent, 10 years), and Virginia's case of the replication (50 percent, 10 years, building over 40 years): each year equal. The year table's taxable value stays whole in an abated year, as the plants' does since session 7515.
- **Exemption:** the thresholds on investment (Louisiana's on the share spent before 1 July 2029, in whole years), permanent jobs, MW (Florida 100) and the first construction year (South Carolina before 2032, Washington before 2035); the years it runs (an end year, a term from the first construction year, Maryland's 20 years at USD 250 million and 10 below); covers equipment, construction or both; the whole rate or the state's part. Every case of the list above equal to the restatement, year by year. Washington's is applied without the county (decision 22); Arizona's, Wisconsin's, Pennsylvania's, Kentucky's and Georgia's tiered thresholds at the largest county's (stated in the note).
- **Equipment's value:** at cost by default (an upper bound, said); Loudoun's schedule typed gives its own arithmetic (decision 8, the cross-check's 9.96 million).

## The four plant types, before and after

- **Base:** `2b958ba16`, the parent of chain 740's first commit (`6708fb1eb`, session 10800); the plants' code and files there are those of `00ffa09a6`, the commit the 32 pins were written from.
- **Runs:** land-based wind, utility PV, natural gas and geothermal, in each of the 51 states the sales tax file holds, at the defaults and four variations (the reader's own rate with a levy, 800 MW from 2032 for 35 years, a 3 percent rate, 5 MW): 1,020 runs, 21 figures each and every year's property, sales and income tax.
- **Result:** 21,420 figures and 147,280 year cells, **0 differences**. The data files changed since (coal, biopower and the trough in `property_rules.json`, `sales_exemptions.json`, `jedi_taxable.json`, `jedi_costs.json`, `eia_capex.json`) and `forecast.ts`'s three new branches move no figure of the four. Severance (the gas plant's callback) is not passed in either tree; its code did not change.

## The 93 announced projects against their documents

Drawn by `random.Random(20261128).sample(k=12)` from all 93 rows: Meta Kansas City (to date), Penzance Berkeley, AWS St. Joseph, Meta Richland 2026, Microsoft Mecklenburg 2015, Meta DeKalb (to date), Meta El Paso, Meta Rosemount, Stargate Milam, Meta Kuna (announcement), AWS Clinton, Cielo Cherokee.

- **What the repository holds of each document:** its title, publisher, date and address, and for each figure the phrase that states it (`says`) inside a quoted sentence (`quote`). The bodies are kept on the data machine (`runs/c740/reads/`), not in git.
- **Checked here for the 12:** every `says` inside its quote; every parse equal to the value (the builder's own parser); qualifiers ("more than", "approximately", "at least", "over") as the quote words them; measures (workers at peak, operational jobs, critical IT capacity) as the quote says; the picker's investment in 2025 dollars (Microsoft's USD 402.4 million of 2015 is 533.2 of 2025); the rows in each median as the file lists them. **12 of 12 consistent.**
- **Across all 93:** the builder's checks (inside the quote, the parse) pass, as its rerun shows.
- **Two readings worth a look, no fault:** Meta's info sheets are laid-out pages whose figures and labels the transcriber paired by order ("$1.2B 2022 100+ Data center investment Broke ground on the Kansas Operational jobs supported in Missouri"); they enter no median. AWS Clinton's USD 1 billion and 100 jobs are one project of a USD 25 billion statewide release, taken as the document words it.
- **Not checked here:** each quote against its kept body: a data request for the data machine.

## One choice changed at a time

Each line changes one choice and keeps every other, by the page's own model. Virginia default unless named.

| Choice the page makes | The other choice | Worth | Said on the page? |
|---|---|---|---|
| Construction workers 833.3 a USD billion (decision 27) | 400.0, the median before Meta's posts | construction jobs -52.0 percent; taxes present value -10.4; earnings present value -32.6 (Texas -40.4) | the hover says "an upper reading"; finding 3 |
| Permanent jobs by MW (decision 2) | by investment, 66.67 a billion | operating jobs +148 percent (322.5 to 800 on site); taxes present value +19.5 | the hover gives both |
| Equipment bought again every 5 years (decision 7) | bought once; every 7 years | taxes present value -66.9 percent (Texas -58.9); +10.7 (more purchases fall after the exemption ends in 2034) | yes |
| Equipment at cost (decision 8) | Loudoun's schedule, Loudoun's rates typed | property present value -62.5 percent; taxes -54.3 | yes |
| CBP's wage for 518210, USD 152,609 (decision 6) | JLARC's "about $100,000" | operating earnings -34.5 percent; taxes present value -5.1 | the note says it; the hover gives 518210's width |
| The exemption applied where the project qualifies | not applied | sales present value +209 percent; taxes +139.8 | yes, a switch |
| The building's taxable share not given | 40 percent | taxes present value +9.8 percent (Mississippi +1.0, its exemption covers construction) | the field says so; the total did not (finding 2) |
| 20 operating years (decision 12) | 30 | taxes present value +36.3 percent | yes |
| 7 percent real (OMB A-94) | 2 percent (A-94 Appendix C) | taxes present value +73.9 percent; earnings +24.5 | yes |
| Median investment a MW, 12.0 (decision 1) | the mean, 17.00 | investment +41.7 percent for the default MW | the note (stale, finding 6) |
| No supply chain or induced effect outside three states (decision 5) | Virginia's, Georgia's or Minnesota's ratios on AWS's Mississippi project | operating jobs x 3.39, 2.92, 2.03; taxes present value +81.2, +49.3, +46.4 percent | the row's hover; not the cells (finding 2) |
| Both documents of a campus in the medians (Richland 2024 and 2026; Amazon's northwest Louisiana February and August 2026) | the earlier left out | construction workers 833.3 to 1,000 a billion; Virginia default's taxes present value +4.0 percent | the row's note in the file |
| The picker's wage and split: CBP's and JLARC's | Beale's own USD 64,000 and two thirds equipment | operating earnings -35.2 percent, income tax -17.4; property present value +13.9 (the building's share 33.3 against 19.6) | no (finding 4) |
| Arizona's standard deduction USD 8,350 (the income file) | 16,100, the federal 2026 amount, if Arizona conforms | Beale's income tax -10.4 percent | a data request |
| Texas and Tennessee: no rule held | the statute's exemption (unread) | up to all of their taxes (100 percent of the present value is that sales tax) | not until finding 1 |

## What a county fiscal analyst's own number would hold that this does not

| Item | Size | From |
|---|---|---|
| The county's own share: property, its part of the sales tax, its consumer utility tax | about 69 percent of the total is local in the Loudoun case (property and the local 0.47 of 5.77 points) | finding 5; the consumer utility tax (58.1-3812) not read |
| Costs of public services (roads, water, emergency services, the board's own staff) | not sized | no such figure is held; the page counts revenue only (finding 5) |
| The county's negotiated agreement (a fee in lieu, a PILOT, an abatement with a schedule) | the abatement input carries a flat share for some years | the reader types it |
| The equipment's depreciation by the county's own schedule | -62.5 percent of property in Loudoun | typed; at cost by default |
| The building's assessed value against its cost | not sized | the building is held at cost unless the reader types years |
| The local sales tax actually sourced to the county (use tax on equipment shipped in) | not sized | the state average local rate stands for it |
| Electricity taxes by price (most states) and Virginia's local consumer utility tax | not sized | no price held; not read |
| Supply chain and induced jobs outside Virginia, Georgia and Minnesota | +46 to +81 percent of taxes in the Mississippi case | BEA's RIMS II sells them (USD 160, named in the licenses file) |

## Findings, largest first

| # | Severity | Finding | Effect, as measured | Fix | Branch |
|---|---|---|---|---|---|
| 1 | High | Texas (the default state) and Tennessee exempt a datacenter's equipment in statutes the ERW could not read; the page said only "none has been read" and the sales cell read as paid | 100 percent of the default Texas taxes (present value USD 1.58 billion) and of Tennessee's (1.85 billion) are that sales tax; ranks 8th and 3rd of 51 | words | `wip/audit-impact-1` |
| 3 | Medium | The default campus holds 10,000 construction workers a year, more than any of 45 documents | at 400 a billion: construction jobs -52 percent, taxes present value -10.4 (Virginia) | figure: ruling | `wip/audit-impact-3` |
| 2 | Medium | On-site-only totals unmarked in 48 states; the lead said JEDI for every state; the total did not name the building's sales tax; the source line named no datacenter source | Mississippi with Virginia's ratios: operating jobs x 3.39, taxes +81 percent; building share 40 percent: +9.8 | words | `wip/audit-impact-2` |
| 4 | Low | A document's own wage and split are not taken, and the page implied stated figures are | Beale: wage 98,701 against the document's 64,000 (+54 percent); taking it: operating earnings -35.2 percent | words; taking them a ruling | `wip/audit-impact-4` |
| 5 | Low | "Taxes, present value" is state and local together and revenue only, unsaid | 69 percent local, 29 the state's (Loudoun case) | words | `wip/audit-impact-5` |
| 6 | Low | The method note's decisions 1 and 2 and its Illinois row quote medians of 54 rows; 13.1's refresh years read as one year early | the note's 10.0, 17.11, 1,100 MW, 550 against 337, 51.2; the file's 12.0, 17.00, 1,000 MW, 800 against 322.5, 66.7 | words | `wip/audit-impact-6` |

- Ranked by severity, then by size. Finding 3 moves printed figures if fixed and is Samuel's ruling (chain 740's decision 27 already asks it). The five words branches are merged, with their tests, in `wip/audit-impact-words`.

## 1. Texas and Tennessee: exemptions in statute, unread, and the page did not say so (High)

- **Where.** `site/lib/dcui.ts`, the field "The state's datacenter exemption" (`dcex`): where no rule is held its hover said "No datacenter sales tax exemption of this state has been read: the sales tax is before exemptions." `site/app/impact/Forecast.tsx`, the A and B row "Sales and use tax", whose hover for a datacenter says "paid, after the state's datacenter exemption where the project meets its thresholds", printed the figure with no mark. `site/app/impact/Datacenter.tsx`, the other-states chart. `site/lib/forecastui.ts` line 189: the default state is Texas.
- **Why it is wrong.** "Has been read" does not tell a reader that a statute exists. The ERW's own ground (`docs/reviews/impact-datacenter-sources-2026-11-26.md` lines 118 and 119) names both: "Texas's data center exemption (Tax Code 151.359) stays unread", "Tennessee's exemption stays unread". A Texas county analyst opening the tool sees USD 2.68 billion of sales tax "paid" by the default campus, every dollar of its taxes, on equipment the statute addresses.
- **How much.** Texas default: present value of taxes USD 1,577,476,774, all of it sales tax before any exemption; USD 2,684,352,000 over the life. Tennessee: USD 1,848,725,830, all sales tax. In "Scenario A in other states" Tennessee is 3rd and Texas 8th of 51. What the exemption would forgo depends on terms not read (thresholds, years): up to all of it.
- **The test.** `tests/test_audit_impact_1.py` on `wip/audit-impact-1`: no rule for either state, the ground names both, and through `dcimpact.ts` (Node) their default taxes are all sales tax, before equal to paid (passes on main); the words test fails on main.
- **The fix on the branch, words only.** `DC_UNREAD_EXEMPTION` in `dcui.ts` names Texas's statute and Tennessee's exemption as unread, in the field's hover, the forgone cell's hover and the forgone row's hover; the sales cell says "before any exemption" wherever no rule is held or the rule is words only (Nevada, Illinois and the others), with the reason on hover; the chart's words say the two bars are before an exemption in statute. Drawn to HTML for Texas, Tennessee beside Virginia, and Nevada, and read.
- **Not done.** Applying either exemption needs its text: a data request.

## 2. On-site-only totals did not say what they leave out (Medium)

- **Where.** `Forecast.tsx`, `dcCellOf` and `dcLeftOut`; `DC_TIP` (the rows' hovers: "elsewhere on site only"); `page.tsx`, the lead's hover ("Jobs, earnings and output are NLR's JEDI models read for every state", "Gross effects of an input-output model") and the source line (JEDI, EIA, the Tax Foundation; no datacenter source).
- **Why it is wrong.** Outside Virginia, Georgia and Minnesota no supply chain or induced figure exists, and the cells for construction and operating jobs, their earnings, the income tax and the earnings' present value are on site only with nothing in the cell. Set beside a Virginia scenario (or a plant, whose JEDI figures hold all three effects), the same project shows a fraction of the jobs for no reason but the state's study. "Taxes, present value" named property and electricity among what it leaves out, not the building's sales tax (left out until a taxable share is typed) nor the income tax of supply chain and induced jobs.
- **How much.** AWS's Mississippi project with Virginia's ratios: operating jobs 1,000 to 3,388.5, income tax present value +97.1 percent, taxes +81.2; with Georgia's +49.3, with Minnesota's +46.4. A building's taxable share of 40 percent: Virginia default's taxes present value +9.8 percent.
- **The test.** `tests/test_audit_impact_2.py` on `wip/audit-impact-2` (the figures pass on main; the words fail on main).
- **The fix on the branch, words only.** The cells say "on site only" where no study is held (not on a zero: a state without income tax); the total says "without property tax, electricity tax, the building's sales tax or supply chain and induced income tax" as each applies; the lead's hover says what a datacenter's figures rest on and that they are on site only outside the three states; the source line names a datacenter's sources. Drawn to HTML and read.

## 3. The default construction workers exceed every document (Medium; a figure)

- **Where.** `dcimpact.ts`, `dcDefaults`: `cons = invest / 1000 x construction_jobs_per_billion.median`; `datacenter_announced.json`, 833.333333 of 25 rows; the note's decision 27.
- **Why it is wrong.** The ratio comes mostly from small campuses (Meta's USD 0.8 to 1 billion campuses count 1,000 to 1,500 at peak); applied to the default USD 12 billion campus it gives 10,000 workers on site in each of two years. No document says so many: of the 45 rows that state a headcount the largest is 8,000 (Paducah, USD 100 billion, period not stated), then 7,500 (Hyperion, USD 50 billion, at peak) and 5,000 (Hyperion's first document). Builders do not scale with the equipment that is most of a large campus's cost.
- **How much.** At 400 a billion (the median before Meta's posts): Virginia default construction jobs 33,635 to 16,145 (-52 percent), income tax over the life -22.8 percent, taxes present value -10.4, earnings present value -32.6; Texas earnings present value -40.4.
- **The test.** `tests/test_audit_impact_3.py` on `wip/audit-impact-3` (passes on main; it records the size).
- **For Samuel's ruling.** Default "left as it is". The other choices (a cap at the largest document's headcount, a median headcount, workers a MW, the 400 of before) each move the construction lines; chain 740's decision 27 holds the same question.

## 4. A document's own wage and split are not taken, unsaid (Low)

- **Where.** `dcui.ts`, `dcProjects` (MW, investment, permanent jobs, construction workers only; a `wage` field on one row is never read); `Datacenter.tsx`, the picker's hover ("a figure it does not state keeps its default", which reads as if a stated one is taken).
- **The rows.** Pima County on Beale (USD 64,000; USD 2.4 billion of 3.6 for equipment), Metrobloks in Clay County, Missouri (USD 95,649; CBP's 106,818 in 2025 dollars), Google in Storey County, Nevada (USD 31.29 an hour), Vantage in Storey County (USD 64 an hour), Facebook in Huntsville (the `wage` field, USD 80,000 of 2018).
- **How much.** Beale with its own wage: operating earnings USD 17.8 million to 11.5 a year (-35.2 percent), income tax over the life -17.4 percent, taxes present value -0.9. With its own split: sales -2.25 percent, property present value +13.9 (with a rate typed).
- **The test.** `tests/test_audit_impact_4.py` on `wip/audit-impact-4`.
- **The fix on the branch, words only:** the picker's hover says a stated wage or split is not taken, with Pima County's example. Taking them is Samuel's ruling.

## 5. "Taxes, present value" is the state's and the locality's together, and revenue only (Low)

- **Where.** `Forecast.tsx`, `DC_TIP.pvtax`; `dcRun`'s `pv.taxes` (property, sales paid, income, electricity).
- **Why it matters.** A county analyst needs the county's part: the property tax is the locality's, the income tax the state's, the sales tax both; no cost of the services the project uses is netted. The lead says "state and local taxes" and the line never said they are one sum.
- **How much.** Google's Virginia investment with Loudoun's rates and schedule typed, a 40 percent building share and 300 MW all year: present value USD 1,486,967,447; property 1,004,378,714 and the local 8.1 percent of the sales tax, about 69 percent; income and the state's part of the sales tax, about 29 percent; electricity (1.5 percent) not split.
- **The test.** `tests/test_audit_impact_5.py` on `wip/audit-impact-5`. **The fix on the branch, words only:** the line's hover says so. A split by level of government would add figures: Samuel's ruling.

## 6. The note's decisions quote medians the file no longer holds (Low)

- **Where.** `docs/methods/forecast.md` 13.4 decisions 1 and 2, 13.5's Illinois row, 13.1's refresh years. Chain 740's own note (`docs/state/note_2026-11-26_window3_c740.md` line 23) likewise gives 1,100 MW and USD 10.0 a MW; that file is chain 740's record and is left as it is.
- **The fix on the branch, words only.** 12.0 and a mean of 17.00 (72 rows); "the 1,000 MW default (USD 12 billion) would be 800 jobs instead of 322.5"; "66.7 permanent jobs a 2025 USD billion"; "5, 10 and 15 years after the first operating year ... the 6th, 11th and 16th operating years, three purchases in 20 years". `tests/test_audit_impact_6.py` on `wip/audit-impact-6`.

## What was checked and found right

- **Every formula of 13.1** against the code: jobs and earnings on site; the three states' ratios (Tables D-3 and D-5; the Carl Vinson Institute's Tables 3 and 4); equipment over the build and at each refresh at its first real cost; the building's sales tax only where its share is given; before, forgone, paid; the state's part of the rate; property by the state's ratios, the reader's rates, the schedule, the building's years and the abatement; income tax per job on the average wage of all effects; Virginia's, Illinois' and Ohio's electricity by monthly blocks, Ohio's lower elective schedule; present values to the first construction year. Right.
- **Dollars:** the investment deflated from its document's year (2026 taken as 2025), wages from 2023; every figure in 2025 dollars, as the page says.
- **The picker:** a document's MW, investment (2025 dollars, to the cent of a million), permanent jobs (unless of a kind not stated) and construction workers; Paducah's and Vantage's investments not taken, with the row's note; to-date rows in no median.
- **The replication** passes 16,010 of 16,010 on today's files.

## Not covered, or left open

- The 43 states' rules other than the three projects' were checked against the code, not each against its statute.
- Ohio's elective kilowatt-hour schedule, Illinois' blocks, and the property ratios of states without a project here: as stated, not re-read.
- The CSV, Python and Stata downloads (`dcfiles.ts`): not re-run (chain 740's `dc-files-check.mjs` covers them).
- The cross-check (13.5): read, not recomputed.

## The deploys of this file (rule 8)

None: this file and its folder are on `wip/audit-impact-doc`, which deploys nothing to production. The words branches change pages that are in review; their landing needs rule 8's snapshot by the main session.
