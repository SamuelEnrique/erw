# Review pack: What a project does for a state

- **Address:** `/impact` (production `https://erw-flame.vercel.app/impact`, opened after `https://erw-flame.vercel.app/internal/open`). The economic impact tool, tool 17 of the platform.
- **Status:** in review, like every page (`site/lib/release.ts`); in the Economics menu under its own line (`site/lib/pages.ts`). A visitor sees the in-review page; the review needs the internal view.
- **Written from:** branch `wip/345-impact` (sessions 345 to 347, 20 October 2026, the third machine), not yet on `main`. The old laptop lands it (`docs/state/review_2026-10-20_third.md`).
- **Numbers:** read from `warehouse/output/nlr_jedi_multipliers.csv` on 20 October 2026, the same rows Supabase holds (5,562; the loader's match line). The default case is land-based wind in Texas.

## 1. What it is for, and for whom

- **The question:** what building and running a power plant does for the economy of the state it is built in: how many jobs, how much in wages (earnings) and how much in goods and services (output), while it is built and each year it runs; and what the state's taxes on it are.
- **For whom:** a state or county official weighing a project, a developer preparing the local case for one, a journalist checking a claim of "thousands of jobs", a student of input-output models.
- **What it gives:** job-years of construction, jobs in each year of operation, earnings and output in the model's dollars, split into on site, supply chain and induced; the swing of each lever; the same project's construction jobs in every state.
- **Default case:** land-based wind in Texas at JEDI's default project (300 MW), cost and local shares: 1,026.68 job-years while it is built and 67.10 jobs in each year it runs; USD 63.46 million of construction earnings (2017 dollars). Texas is 12th of 51 for this project's construction jobs.
- **What it is:** NLR's own JEDI models, read for every state by their own formulas, times the reader's project. Gross effects of an input-output model.
- **What it is not:** a net effect, a forecast of hiring, a fiscal note, or advice. No sentence on the page says whether to build.
- **Three questions on the page:** "How many jobs?", "What does it pay the state?", "What matters most?" (the battery page's layout, session 208).

## 2. The model, step by step

1. **The workbooks come in.** Four of NLR's JEDI workbooks, the current public release of each, kept as they came in `warehouse/raw/nlr_jedi/` (`pull()` in `warehouse/connectors/jedi_multipliers.py`; nine requests of a ceiling of twelve, logged in `runs/s345/requests.csv`).
2. **Each workbook is computed from its constants** (`fresh()` in `warehouse/connectors/jedi_recalc.py`, pycel in `.venv-jedi`): every formula cell is emptied and computed again, and the saved project's 30 summary figures must come back exactly before anything is written (`run()`).
3. **Excel's functions pycel lacks** are written out from Excel's definitions (`ispmt()`, `ipmt()`, `ppmt()`, `median()`, `exp()` in `jedi_recalc.py`), and the sheets' own names are resolved (`local_names()`).
4. **Every location of the model's own list** is set as Project Location and the workbook computed again (`run()`), with the PV model's System Application set to its own Utility option (`MODELS["utility_pv"]["settings"]`). Each total must be the sum of its three lines (`identity()`); a location whose answer is an Excel error is kept as that (`errors`).
5. **Per MW** (`rows_for()` in `jedi_multipliers.py`): each summary line divided by the default project's MW; the project's MW and each phase's local share become rows of their own.
6. **The table is written and checked** (`main()`; `warehouse/validate/erw_validate.py`; `warehouse/metadata/build_coverage.py --only`), then loaded (`warehouse/supabase/load.py --only`), drafted to Redivis (`warehouse/redivis/upload.py --tables`) and archived (`warehouse/archive/archive.py write --tables`), each under the data lock.
7. **The tax rules** are the /severance page's rules as a table, and seven rows that say no property-tax rule is held (`severance_rows()`, `property_rows()` in `warehouse/derived/impact_tax_rules.py`).
8. **The page reads** the 27 rows of the reader's technology and state, every state's construction jobs, and the state's tax rules (`Impact()` in `site/app/impact/page.tsx`).
9. **The reader's project** (`stat()` and `factor()` in `site/lib/impact.ts`): JEDI's per-MW figure times MW, times the local content's percent of JEDI's shares, and for construction times the capital cost's percent of JEDI's default.
10. **Every figure is checked** (`site/scripts/check-values.mjs`, family `impact|`): the script reads the same rows itself and recomputes each figure with the page's own `stat()`; JEDI's per-MW figures and shares are `series|` keys read directly.

## 3. Every assumption

| Assumption | Default | Source |
|---|---|---|
| Technology | Land-based wind | The first of the four JEDI models held; any of the four may be picked |
| State | Texas | One of the three states whose tax rules are held; any of 51 or the nation may be picked |
| Project size | JEDI's default project: 300 MW wind, 100 MW (DC) solar, 500 MW gas, 12.23 MW geothermal | Each workbook's saved project (`project_mw` rows, `SummaryResults!C4`, `C6`, `Summary Results!B7`) |
| Capital cost | 100 percent of JEDI's default | The workbook's own cost for its default project, in its dollar year |
| Local content | 100 percent of JEDI's shares (Texas wind: 0.22 of construction spending, 0.23 of direct operating cost) | JEDI's default share of each cost line (`local_share` rows, JEDI's local spending over the phase's cost) |
| Life | None: JEDI states no plant life | The page adds up the operating years only when the reader gives one (Samuel's question 3) |
| Abatement | Off, and it applies nothing | No property-tax statute is held (`impact_tax_rules`, `no_rule_held`) |
| Multipliers | Each state's own, from IMPLAN | The workbook's `Multipliers` sheet: wind 2016, PV 2019, gas 2014, geothermal 2014 (its note says 2012) state data |
| Dollars | Each model's own year: wind 2017, the others 2010 | The workbook's Money Value; nothing is converted |
| Utility-scale solar | The PV model with its System Application set to Utility | The model's own option and its own utility defaults (the workbook is saved with residential systems) |
| One FTE | 2,080 hours in a year | JEDI's notes under its summary |
| Proportional levers | Every effect proportional to spending | JEDI's input-output arithmetic; the local content's single factor is the page's one approximation |
| Severance | Not computed for a plant | A plant produces no oil or gas (`x_applies_to` of every severance row) |

## 4. The cross-checks

| What was compared | With what | Result |
|---|---|---|
| Wind's saved project (Connecticut), 30 summary figures, computed from the constants | The figures the workbook saved | Equal to one part in a billion, every one |
| PV's saved project (Arizona, residential), 30 figures | The saved figures | Equal, every one |
| Gas's saved project (Wyoming), 30 figures | The saved figures | Equal, every one |
| Geothermal's saved project (Idaho), 30 figures | The saved figures | Equal, every one |
| Each location's total, both phases, three measures | Its on site, supply chain and induced lines | Equal at every one of 206 locations (`identity()`; `tests/test_session345.py` on the table) |
| `ISPMT`, `IPMT` (two), `PPMT` (two) as written | Excel's documented examples (-64,814.81; -66.67; -292.45; -75.62; -27,598.05) | Equal to the cent |
| A first version that only changed the location | The per-location sum | It gave every state Connecticut's supply chain and induced jobs; the check now stops it |
| The national row of each model | Every state's | Larger for every model (all spending counted as local) |
| The table's 5,562 rows | Supabase's rows | Equal (the loader's match line, 20 October) |
| The table's 5,562 rows | Redivis's draft, `count(*)` | Equal |
| The tax rules' 42 held rows | `site/data/severance_rules.json`'s rules and Louisiana's two oil variants | Equal (`tests/test_session346.py`) |
| The page's figures at four addresses | check-values' own read and the page's `stat()` | See the session 347 report's checks |

## 5. The edge cases tested

| Case | What the page does |
|---|---|
| Battery storage | Listed, greyed and not selectable: "not modeled: NLR publishes no JEDI model for it"; an address asking for it says so in the status line and shows wind |
| Natural gas in the District of Columbia or Hawaii | JEDI's own answer is `#DIV/0!`: no figure, and a line that says why |
| A size, cost, share or life outside its bounds | Brought inside them, with a line saying what was typed and what is used |
| A state with no tax rules held (any but TX, LA, NM) | "No rule is held, so no tax figure is shown" |
| The United States (national) | Every figure national; the state chart and rank are not drawn |
| No life given | The life column says "no life given"; the life lever shows five years of operation |
| The abatement scenario on | Says it applies nothing, as no rule is held |

## 6. What the model cannot see, ranked

1. **The counterfactual.** Gross effects: nothing displaced, no other plant's jobs lost to the power this one sells.
2. **Today's costs.** JEDI's default costs are of 2010 to 2017 projects; every effect is proportional to spending, so a more expensive build today counts more. The capital cost lever is the reader's way to say so.
3. **Tight markets.** Workers and materials are always there at today's prices; a state at full employment would see wages rise or work leave.
4. **Property tax.** No statute held; the tax a plant pays its county is the largest it pays, and the page states none.
5. **Who owns it.** Profits leave the state when the owners are elsewhere; JEDI counts wages and local purchases, and sets the saved projects' debt and equity payments local share to 0.
6. **Scale.** Per MW of the default project: a much larger or smaller plant is not that project scaled (geothermal's economies of scale most of all).
7. **The line-by-line local content.** The page scales every line of a phase by one factor; JEDI would apply the reader's share line by line.
8. **Batteries.** No JEDI model.

## 7. The ten hardest questions

### 1. A developer says 3,000 construction jobs. The page says about 1,000 job-years. Who is right?
Both may be: a job-year is one full-time job for a year. 3,000 people on a site for four months each is 1,000 job-years. The page counts as JEDI counts.

### 2. These are gross effects. What would the net be?
Lower, by what the land, money and workers would have done otherwise. JEDI does not estimate it; no number is offered.

### 3. JEDI's costs are years old. Are the jobs too low?
At today's higher costs JEDI would count more, in proportion. Set the capital cost above 100 to see it; the multipliers themselves move slowly.

### 4. Why is Texas 12th and Maine first for a wind farm?
Each state's own businesses supply a different share of what the plant buys. JEDI's Maine multipliers keep more of the supply chain and induced spending in the state.

### 5. The national row is three times any state's. Is that double counting?
No: nationally, spending anywhere in the country is local, so more of it stays in. It is the national effect, not a sum of states.

### 6. Why is there no battery?
NLR publishes no JEDI model for battery storage, and the ERW does not make one up.

### 7. Why no property tax, the tax that matters most?
The ERW holds no statute for it in any of the three states; the chain allowed no request. Question 2 below asks to pull them.

### 8. How can the page change a workbook's state without Excel?
pycel evaluates the workbook's own formulas. The proof is that the saved project, computed from the constants, gives back all 30 of its saved figures exactly, in all four models.

### 9. Is the local content lever exact?
No: it scales a phase's lines by one factor where JEDI applies a share to each line. At 100 percent it is exact; away from 100 it is the page's approximation, said in its hover and the method.

### 10. Are the four technologies comparable?
Per MW, in each model's own dollars and with each model's own default project; wind is 2017 dollars and the others 2010. A comparison should deflate first; the page converts nothing.

## 8. What Samuel's Stata run must reproduce

No do-file of this page is written yet. The table's Stata reader (`/api/download?table=nlr_jedi_multipliers&as=do`) loads the rows; the default case's figures follow from them:

```stata
* the table, as the page's download gives it (the reader keeps the "#" lines)
do nlr_jedi_multipliers.do
keep if strpos(entity, "nlr_jedi:land_based_wind:tx:") == 1
* the default project's MW (300)
list value if variable == "project_mw"
* 1,026.68 job-years built; 67.10 jobs each year; USD 63.46 million of construction earnings (2017 dollars)
display 3.42226 * 300
display 0.223679 * 300
display 211542.557943 * 300
```

The same in Python, from the table's CSV: `value * 300` on the rows `nlr_jedi:land_based_wind:tx:construction:total` (jobs, earnings) and `...:operations:total` (jobs).

## 9. Questions only Samuel can answer

1. **The tax rules' terms.** The Texas Comptroller's, the Louisiana Legislature's and Department of Revenue's, and New Mexico's Taxation and Revenue Department's pages were never read for their terms, so `impact_tax_rules` is "not settled" and not offered for download. (a) a session reads them, one request each; (b) rule the tables public as state law; (c) keep them held.
2. **Pull the property-tax statutes?** Texas Tax Code chapters 312 and 313, Louisiana's Industrial Tax Exemption Program rules and New Mexico's Industrial Revenue Bond Act are named by the chain prompt and held nowhere. (a) a data session with a ceiling reads each from the state's own statute page; (b) leave the question as "no rule held".
3. **A default life?** JEDI states none. (a) the generator page's cited lives (Lazard: wind 30, solar 35 years) for those two, none for gas and geothermal; (b) keep no default.
4. **Severance on a gas plant's fuel?** JEDI's gas model holds a "fuel produced locally" share (0 in its saved project). (a) a scenario: the in-state share of the fuel, the heat rate and capacity factor, the well-head price and the state's rate; (b) no: severance is the wells' tax.
5. **Utility-scale solar as the PV model's Utility option.** (a) keep; (b) show the saved residential project instead; (c) both, as two technologies.
6. **The wind release.** NLR offers a Beta W10.30.20 as a program, not a workbook; the page reads the workbook W9.14.18. (a) keep; (b) ask JEDI support for the beta's workbook.
7. **One dollar year?** (a) keep each model's own; (b) deflate all to one year by a named index.
8. **The local content lever.** (a) keep the one-factor approximation; (b) a data session computes JEDI at a few shares line by line, exactly.
9. **More models?** NLR also publishes coal, conventional hydro, CSP, marine, petroleum, transmission line, offshore and distributed wind models. (a) add the transmission line and offshore wind; (b) others; (c) none.
10. **IMPLAN.** The multipliers inside the workbooks are IMPLAN's; the table holds JEDI's results per MW, not the multipliers. (a) public as NLR's notice allows; (b) ask NLR whether results by state may be republished.

## Where every number comes from

- **Every jobs, earnings and output figure, every project MW and local share:** `nlr_jedi_multipliers` (`warehouse/connectors/jedi_multipliers.py`, from `jedi_recalc.py`'s files), read on the page from Supabase and checked by `check-values.mjs`.
- **The tax rules:** `impact_tax_rules` (`warehouse/derived/impact_tax_rules.py`, from `site/data/severance_rules.json` of sessions 40 and 41).
- **The default case in part 1:** computed from the table's CSV on 20 October 2026 (Texas wind, 300 MW: per MW 3.42226, 0.223679 and USD 211,542.56).
- **The terms:** NLR's notice at `https://www.nlr.gov/disclaimer` (license read 65, the same page read again in session 345).
- **The method:** `docs/methods/economic_impact.md`, sections 1 and 2.
