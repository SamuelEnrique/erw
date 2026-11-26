# `/impact` with the datacenter: five readers' cases on a local production build (chain 740, session 10808, 26 November 2026)

Energy Research Warehouse (ERW). Branch `wip/c740-impact-datacenter` at `194d55f56` (origin/main merged at 12:14 UTC), built in lab-desktop's worktree `erw-w3-c740` under the build lock (`c740-w3-build`, 12:15 to 12:29 UTC; three builds, 81, 56 and about 60 s), served on port 3741, read with headless Chrome by the DevTools protocol at 1280 and 390 px with the review cookie (`runs/c740/read_page.mjs`, screenshots under `runs/c740/shots3/`, not in git). Every case, both widths: no sideways scroll, no console error or exception. `site/scripts/check-values.mjs` on every `/impact` address (the nine of the floors file, two of them new): 1,506 of 1,506 values match.

## The cases

| Reader | Address (what they set) | What they read |
|---|---|---|
| A county commissioner weighing an abatement (Richland Parish) | Meta's Richland Parish project picked (LED, 13 July 2026: 5,000 MW, USD 50 billion, 1,000 operational jobs, 7,500 construction workers at peak), a 5-year build, the parish's rates typed as 10 percent of assessed value; B the same with 50 percent abated for 10 years | property tax in the first operating year USD 609.5 million (A) against 304.8 million (B); over the life USD 12.19 against 9.14 billion; the taxes' present value USD 5.89 against 4.26 billion. The hover gives Louisiana's 10 and 15 percent assessment and says the millage is the parish's. The sales tax line shows the exemption's cost beside it: USD 13.82 billion before, 10.36 billion forgone (R.S. 47:305.73, 20 years) |
| A legislator's aide reading the exemption's cost (Virginia) | CleanArc's Caroline County campus picked (VEDP, November 2025: nearly 1 GW, USD 3 billion, 50 jobs); B the same project with the exemption not applied | forgone USD 236.1 million (A) and USD 0 (B, the scenario's choice); the taxes' present value USD 108.8 against 296.5 million; the hover quotes 58.1-609.3(18)'s thresholds and says the wage test is not checked |
| A developer comparing two states | 600 MW, USD 4 billion, 125 permanent jobs, 1,000 construction workers, in Virginia (A) and Georgia (B) | Virginia: forgone USD 314.8 million, supply chain and induced jobs by JLARC's ratios (3,364 construction job-years, 424 operating jobs); Georgia: on site only (2,000; 125), forgone "none" with the reason (its thresholds were not read), sales tax USD 824.9 million before exemptions |
| A utility regulator | 1,000 MW, USD 11 billion, 6,000,000 MWh a year bought in Virginia; B a gas plant of EIA's case size in Virginia | the consumption tax USD 5.3 million a year (58.1-2900's blocks); the datacenter's 1,037 operating jobs beside the gas plant's 183; the plant's figures as before, the datacenter's own lines "none" for the plant |
| A student | `/impact?tech=datacenter&state=wv` (every default) | 1,000 MW, USD 11 billion, 306 permanent jobs, 5,500 construction job-years, sales tax USD 1.98 billion before exemptions, forgone and electricity "not held" with their reasons (West Virginia's code host does not answer); every default grey with its source and range on hover |

The page as it opens (Texas wind) reads exactly as before: 515 construction jobs, USD 41 million of construction earnings, taxes' present value USD 19.9 million (the pins).

## Faults found and fixed (session 10808, commit `194d55f56`)

1. **The forgone line read "USD 0" where no exemption applies.** West Virginia (no statute read) and Georgia (held as words) showed USD 0, as if a statute gave nothing. Now "not held" where none is read and "none" where one is read but not applied, each with its reason on hover; USD 0 only where the scenario turned an applicable exemption off.
2. **The size field showed the typed MW as its own default.** Its default is now the announced projects' median whatever is typed (the investment's and jobs' defaults still follow the MW, by design).
3. **"In other states" laid the reader's local property rate on every state's full cost** (Louisiana's 10 and 15 percent assessment lost elsewhere: bars about eight times Louisiana's). The chart now compares sales, income and electricity taxes, whose rates are statewide, and says property is left out because its rates are local.
4. **A discretionary rule's reason named Nevada's case for Georgia and Utah.** The words now say the relief is held as words only, its hover saying why.

## Not changed, noted

- The year chart's labels crowd at 22 or more years (the plants' chart does the same; a shared component, not this chain's to change).
- Construction workers at an announced peak are held in every construction year (an upper reading of job-years), said in the field's hover and in `forecast.md` 13.4.

## Three more readers (session 10820, on the build of `3e15b9395`, read at 14:47 UTC)

| Reader | What they set | What the page gives, and whether it answers them |
|---|---|---|
| A state budget analyst comparing two neighbours | 600 MW, USD 6 billion, 500 permanent jobs, the building's taxable share 40 percent, in Arkansas (A) and Oklahoma (B) | sales tax before exemptions USD 1.6 billion and 1.48 billion; forgone USD 1.09 billion (Act 548, the state's 6.5 percent, equipment and building) and 736.6 million (the evaluation's no-threshold exemption, the state's 4.5 percent, equipment only); each hover says only the state's part is applied. Answers them, with the state-rate caveat in sight |
| A utility planner in the Ohio valley | 600 MW, USD 6 billion, 200 jobs, 5,000,000 MWh a year, 7 percent property rates, in Ohio (A) and Illinois (B) | electricity tax USD 9.5 million a year in Ohio (the self-assessing schedule, the lower) and 10.2 million in Illinois (ten blocks); property: Ohio's building 28.8 million at 35 percent and its equipment USD 0 (untaxed since 2009); Illinois' building 82.3 million at one third and its equipment 286.4 million at the typed rate, which the hover says to leave blank unless the county taxes it. Answers them, the Illinois equipment line hanging on the reader's choice |
| A South Carolina county assessor | 600 MW, USD 2 billion, 200 jobs, 32 percent rates (320 mills), in South Carolina (A) and Kansas (B) at 13 percent | South Carolina: building USD 7.5 million at 6 percent, equipment 45.8 million at 10.5 percent; Kansas: building 12.7 million at 25 percent, equipment USD 0 (79-223). The 32 percent rate is accepted (the fields took up to 20 before). Answers them; a fee in lieu goes in the abatement input |

No fault found in these three. The Illinois equipment line is a reader's choice by design (no page read says whether the county taxes it).
