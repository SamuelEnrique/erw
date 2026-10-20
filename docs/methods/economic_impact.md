# Economic impact: what a project does for a state

Energy Research Warehouse (ERW), tool 17 of the platform (`docs/platform-tools.md`), the economic impact tool
(`/impact`, in review). Sessions 345 to 347, 20 October 2026. This note says where each of the tool's numbers comes
from, what the models behind them assume, and what they cannot see. Section 1 is the jobs, earnings and output
(`nlr_jedi_multipliers`); section 2 is the tax side (`impact_tax_rules`).

## 1. Jobs, earnings and output: NLR's JEDI models

### What JEDI is

The Jobs and Economic Development Impact (JEDI) models are spreadsheets that the National Laboratory of the Rockies
(NLR, formerly the National Renewable Energy Laboratory, NREL) publishes free, one for each kind of plant
(https://www.nlr.gov/analysis/jedi/models). The user enters a project (where it is, how large, what it costs) and
the model says what building it and running it does for that state's economy. It gives three measures:

- **Jobs**: full-time-equivalent jobs. One FTE is 2,080 hours of work in a year. A build's jobs are counted over the
  whole construction period, so they are job-years (`FTE-year/MW`): 3 job-years can be three people for a year or one
  person for three years. Operating jobs are the jobs held in each year the plant runs (`FTE/MW`).
- **Earnings**: wages, salaries and benefits paid to those workers (`USD/MW` for a build, `USD/MW-year` while it runs).
- **Output**: the value of all the goods and services produced in the state because of the project, the widest
  measure (the same units as earnings).

Each measure is given in three parts, which the table keeps apart (`x_effect`):

| JEDI's line | `x_effect` | The economist's word | What it counts |
|---|---|---|---|
| Project development and onsite labor | `onsite` | direct | the people on the site: construction crews, then the plant's own staff |
| Turbine (or module, or power generation) and supply chain | `supply_chain` | indirect | the state's businesses that sell to the project: concrete, steel, equipment, services, and the businesses that sell to them |
| Induced | `induced` | induced | the spending of the wages above in the state's shops, restaurants and services |
| Total | `total` | | the three added; the table checks that JEDI's total is their sum at every location |

### What JEDI assumes

JEDI is an **input-output model**. It takes the project's spending, line by line (turbines, concrete, labor, legal
services, insurance), keeps the part of each line spent inside the state (the **local share**), and multiplies each
local dollar by a multiplier: how many jobs, how much earnings and output a million dollars of new demand for that
industry makes in that state. The multipliers come from IMPLAN, a commercial input-output database, one set per state
(the hidden sheet `Multipliers` of each workbook, by industry). Behind that are four assumptions a reader should keep
in mind:

1. **Fixed recipes.** An industry always buys the same mix of inputs per dollar of output, whatever the size of the
   project. Doubling the spending doubles every effect.
2. **No limits.** Workers, materials and equipment are always there to be had at today's prices. A state whose
   construction workers are all busy would in fact see wages rise or work move elsewhere; JEDI sees neither.
3. **Nothing displaced.** Every dollar is new. JEDI does not ask what the land, the capital or the workers would have
   done otherwise, nor whether the power the plant sells replaces power from another plant in the same state.
4. **Local shares are JEDI's defaults** unless the user changes them: the share of each line bought in the state, set
   by JEDI's authors for a typical project (for wind, 90% of construction materials, 0% of turbines). The table holds
   them as JEDI applies them, and `x_local_share` gives the result for each phase: JEDI's local spending divided by the
   project's cost (construction) or its direct operating cost (operations), with the cells it was read from.

### What JEDI cannot see

- **The counterfactual.** These are gross effects, not net ones: what the project adds, not what it adds minus what
  would have happened without it.
- **Who owns the plant.** Profits paid to owners outside the state leave it; JEDI's induced effects count only wages
  and local spending, and the debt and equity payments of the saved projects are set to 0 local share.
- **Taxes as policy.** JEDI's property-tax line uses its own default rate and "assumes no tax abatement" (the gas
  workbook's note). The tax side of this tool is section 2, from the statutes, not from JEDI.
- **Age.** The multipliers are from IMPLAN data of 2014 to 2019, and the default costs from projects of 2010 to 2017
  (the table below). An economy's structure moves slowly, but costs have moved: a wind farm built today costs more per
  kW than JEDI's default, and since every effect is proportional to spending, JEDI's per-MW figures at its own default
  cost are a floor for today's prices, not a forecast.
- **Scale.** The figures are per MW of JEDI's default project. Where costs fall with size (the geothermal model's
  economies of scale, a wind farm's fixed costs), a much larger or smaller project is not that project scaled.
- **Batteries.** NLR publishes no JEDI model for battery storage (the thirteen models on its page, read 20 October
  2026, have none). The table has no battery row, and the tool says so; no figure is made up.

### The four models held

| `x_technology` | NLR's model | Release (the About sheet) | File | Saved project | Per MW of | Dollar year | Multipliers (IMPLAN) |
|---|---|---|---|---|---|---|---|
| `land_based_wind` | JEDI Land-based Wind Model | W9.14.18 | `01d-jedi-land-based-wind-model-rel-w6-28-19.xlsm` | 300 MW in Connecticut, built 2017 | nameplate MW (300) | 2017 | 2016 state data |
| `utility_pv` | JEDI Photovoltaics Model | PV05.20.21 | `jedi-pv-model.xlsm` | 500 kW of residential systems in Arizona; read with System Application set to Utility | DC nameplate MW (100, JEDI's utility default) | 2010 | 2019 state data |
| `natural_gas` | JEDI Natural Gas Model | NG4.17.17 | `01d-jedi-ngas-model_rel-ng4-17-17.xlsm` | 500 MW in Wyoming, construction from 2014 | nameplate MW (500) | 2010 | 2014 state data |
| `geothermal` | JEDI Geothermal Model | GT12.23.16 | `01d-jedi-geothermal-model-rel-gt12-23-16.xlsm` | 10 MW net (12.23 MW nameplate) binary hydrothermal plant in Idaho | nameplate MW (12.23) | 2010 | Year of Data 2014; the sheet's note says 2012 state data |

The land-based wind page also offers a "Beta" release W10.30.20 as a Windows or Mac program in a zip file. It is a
program, not a workbook, and the ERW runs no publisher's program; the workbook is the release the ERW reads. The wind
file's name says W6.28.19 while its About sheet says W9.14.18; the table records the About sheet's number and the file
name both. NLR's offshore wind model (an installer) and its distributed wind model are not read.

Each workbook's dollars are its own dollar year (`x_dollar_year`). The table converts nothing: a reader who adds the
models together, or compares them, deflates them first.

### How the ERW read them: each workbook's own formulas, for every state

A JEDI workbook is saved with one project in one state, and holds the results of that project only. A per-MW figure
for another state is therefore what the workbook itself gives once its Project Location is that state. Two scripts
make the table:

1. `warehouse/connectors/jedi_recalc.py` evaluates each workbook's own formulas with pycel, a Python reader of Excel
   formulas (no Excel, no macro), in an environment of its own (`.venv-jedi`, outside git; pycel needs an older
   networkx than the repository's). It first computes the saved project **from the workbook's constants** (every
   formula cell emptied and computed again, 12,798 to 21,976 cells a model) and refuses to write anything unless
   all 30 saved figures of the summary come back exactly (to one part in a billion). It then sets Project Location to
   each location of the model's own pull-down list, computes again from the constants, and checks that each total is
   the sum of its three lines. Nothing else is changed, except the PV model's System Application, set to its own
   "Utility" option (the tool asks about utility-scale solar; the workbook is saved with a residential project).
2. `warehouse/connectors/jedi_multipliers.py` divides each summary line by the project's MW and writes the table.

What the first script had to do that a reader of its code should know:

- **Four Excel functions pycel lacks** are written out in the script from Excel's own definitions, each checked against
  Excel's documented examples: `ISPMT`, `IPMT`, `PPMT` (the models' loan schedules) and `MEDIAN` (a wind default), with
  `EXP`, which pycel 1.0b30 does not have.
- **A name scoped to one sheet.** The wind, PV and gas models read `ProjectData!_xlnm.Print_Area`, which their
  ProjectData sheet defines as its own year-of-construction cell. pycel does not resolve such names; the script writes
  each one as the address the sheet defines, in memory, and stops if any is left.
- **pycel's saved values.** pycel builds each formula cell holding the value the file saved and computes it only when
  that value is emptied; a range read before its cells holds the saved values too. A first version of the script that
  only changed the location gave every state Connecticut's supply chain and induced jobs. The script now empties every
  formula cell before each computation; the per-location sum check would catch the old fault.

### What the table holds, and what it does not

`nlr_jedi_multipliers`: 5,562 rows. Four technologies, 52 locations each (the 50 states, the District of Columbia and
the United States as a whole; the gas model 50, below), and for each location 27 rows: two phases, four effects and
three measures (24 figures), the default project's MW (`<technology>:<state>:all:project`, variable `project_mw`) and
each phase's local share (`<technology>:<state>:<phase>:spending`, variable `local_share`, a ratio). The last three
are rows of their own because the site reads only a row's entity, variable, time and value from the live set (session
347). The `UNITED STATES` row is JEDI's national
figure (state blank, `geo` US): spending anywhere in the country counts as local, so it is far larger than any state's.
For the national rows of the gas and geothermal models JEDI's local spending exceeds the project's cost
(`x_local_share` 1.04 and 1.01); the table gives JEDI's lines as they stand.

Not written, by rule:

- **The gas model at the District of Columbia and Hawaii**: JEDI's own answer there is `#DIV/0!` in the summary's
  lines (the cause inside the workbook was not traced). No row; the tool says JEDI gives no figure there.
- **Battery storage**: no model.
- **Value added**, JEDI's fourth measure: the prompt asked for jobs, earnings and output; the workbooks hold it in
  column E of the same lines if a later session wants it.

### Terms

NLR's data terms (https://www.nlr.gov/disclaimer, read on 20 October 2026, the same page and SHA-256 as license read
65 of `docs/licenses.md`): "The user is granted the right, without any fee or cost, to use or copy the Data, provided
that this entire notice appears in all copies of the Data." The user also credits the U.S. Department of Energy
(DOE)/NLR/ALLIANCE, the Data are as is, and DOE/NLR/ALLIANCE's names are not used to endorse anything. The table's
header carries the notice. The workbooks hold no user agreement tab of their own (the gas and geothermal FAQ sheets
mention one accepted at download; the download pages ask for none today). The multipliers inside the workbooks are
IMPLAN's; the table holds JEDI's results per MW, not the multipliers themselves.

## 2. The tax side: severance and property tax

`impact_tax_rules` (session 346): 49 rows in the events shape, one row per rule, every row with its citation. Built by
`warehouse/derived/impact_tax_rules.py` from what the repository already holds; it made no request.

### Severance: the rules the /severance page holds

The 42 rows with status `held` are the severance rules of Texas, Louisiana and New Mexico exactly as
`site/data/severance_rules.json` holds them (sessions 40 and 41, every rate citing a page whose text states it, read as
text on 30 September 2026): 14 base rates and 2 more rows for Louisiana's oil rate by the well's completion date
(beside the base row that names them), 2 Texas fees, and 24 reduced rates or exemptions. Each row keeps the page's own sentence
(`x_quote`), and where the page held one the statute's section and words (`x_code_section`, `x_code_quote`). Nothing was
read again and no rate was changed; a reader checks a row against the page at `source_url`.

`event_date` is the effective date the citation gives when it gives one as a date (Texas's oil tax: 1951-09-01). Where
it gives words instead ("report periods September 2015 and later"), the date is the day the rule was read, 30
September 2026, and `x_date_kind` says so.

**What the economic impact tool does with them.** Severance is a tax on oil and gas taken out of the ground. None of
the tool's four technologies produces oil or gas: a gas plant burns gas that wells produce, and those wells pay the
severance tax, whoever buys the gas. The tool therefore states the rules and computes no severance for a plant
(`x_applies_to`). A severance figure for the fuel a gas plant burns would need the share of its gas produced in the
state, the well-head price and the wells' own exemptions; JEDI's gas model holds a "fuel produced locally" share (0 in
its saved project), and joining the two is a question for Samuel (the review pack, section 9).

### Property tax on a generating project: no rule held

A power plant's largest tax to a state and its counties is usually property tax, and the abatements the prompt names
(Texas Tax Code chapters 312 and 313, Louisiana's Industrial Tax Exemption Program, New Mexico's Industrial Revenue
Bonds) change it most. **No public statute on any of them is held in the repository.** Session 346 searched `docs/`,
`site/data/`, `warehouse/metadata/` and `archive/sessions/` on 20 October 2026: the only property-tax rules held are New
Mexico's ad valorem tax on oil and gas production and its equipment tax, which the severance rows above already hold.
The chain allowed no request, so no statute was read.

Each treatment is therefore a row with status `no_rule_held` (7 rows: the general property tax of a plant in each of
the three states, and the four programs). Such a row states no rate, no abatement and no figure. The tool shows "no
rule held" where a tax figure would stand, and its abatement scenario, which stays off by default, has nothing to
apply until a statute is held.

JEDI's own property-tax line is not used in its place: JEDI's wind workbook says it "does not currently have default
data for taxes per MW", and a tax figure on this page comes from a statute or does not appear.

### Terms

The pages are state statutes and the agencies' own pages. Their publishers' terms of reuse were not read (no request
was allowed), so `docs/licenses.md` lists `impact_tax_rules` as "not settled" and the tool does not offer it for
download until a person rules or the terms are read. The /severance page has cited the same pages since session 40.
