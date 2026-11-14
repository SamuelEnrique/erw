# Session 3938 report: the forecast tool's data requests

Energy Research Warehouse (ERW). Chain 267, data machine (lab-desktop), 14 November 2026, 10:57 to 11:12 UTC. Opus 5.5. Model spend USD 0. Requests: EIA's API (one by hand to read GDPDIUS, then the connector's 5).

**First, a loss this chain caused:** session 3921 removed the worktree `erw-w4-4200` (its branch was in main). Window 4 (chain 239) kept its `runs/w4/` there: the request log `probe.csv` and `eia_requests.csv`, the four JEDI workbooks and the pycel recalculation. `runs/` is git-ignored, so `git worktree remove` took them without a warning. The committed forecast files keep every value with its source and request number; the logs and downloads are gone. A memory note now says to list a worktree's ignored files first.

## Request 1: `eia_steo_forecasts`, GDPDIUS (done)

- **The connector** reads the GDP implicit price deflator annual from 2009 (one more request): 19 years to 2027, unit `index` ("Index, 2017 = 100"), `freq` P1Y, a year from the release's own on marked forecast.
- **A fault found on the way:** the table keeps each STEO release (vintage), and the release of 10 November 2026 is the second. The header lacked decision 77's words ("Revisions: kept, one row per vintage"), so the validator refused 10,176 duplicate keys and nothing was archived. The words added; the table rewritten: 10,195 rows (the October and November releases), validated, archived, in coverage. The daily run would have failed the same way.
- **Test 3938** (2 tests); the four STEO test files: 45 passed. Held from the live catalogue (`catalogue_hold`): no load.

## Request 2: JEDI's construction cost in `nlr_jedi_multipliers` (stopped)

- **Cannot be built here now:** the table's connector needs `jedi_recalc.py`'s files (`warehouse/raw/nlr_jedi/recalc/`), which are on no machine: this machine never held them, and window 4's copy under `runs/w4/` went with its worktree (above). Rebuilding needs the four JEDI workbooks downloaded again and the pycel environment. The forecast keeps reading `site/data/forecast/jedi_costs.json` (committed, checked against the table by `jedi_costs.py`).

## Request 3: the property tax rules in `impact_tax_rules` (done, wider than asked)

- **`warehouse/derived/impact_tax_rules.py`** now reads `site/data/forecast/property_rules.json` beside the severance rules: **81 rules of 50 states and DC** (the file grew from the five states the request named), each with its statute's or agency's words, address and read date. One source entry (`forecast:property_rules`), each row's own address in `source_url`.
- **Written under the data lock:** 130 rows (123 held, 7 no rule held), validated, archived (81 new), in coverage; license records regenerated (the table stays "license needed" since session 4103).
- **The patch of the catalogue files conflicted** with the branch's earlier rows; resolved by taking the branch's files and applying the table's own lines only.

## Request 4: `forecast_parameters` (not reached)

- A new table from `eia_capex.json`, `jedi_taxable.json` and `gas.json`: carried to file 272's data requests.

## Request 5: Texas property tax rates by taxing unit (stopped)

- **comptroller.texas.gov's robots file** reads `Disallow: /*/` (read 2038, licenses request 27): under the wildcard reading it refuses nearly every path, so the Comptroller's rate and levy data is not read. No request made.

## Decisions made without you

- **`impact_tax_rules` takes every rule the forecast's file holds,** not only the five states named: the file is the record, and the table is held.
- **The 20 October no-rule rows for Texas, Louisiana and New Mexico are kept** as they were written (they name specific programs: chapters 312 and 313, ITEP, IRBs); the file's own Texas, Louisiana and New Mexico rules sit beside them.

## For Samuel's ruling

- **Several of the forecast file's Texas rows cite comptroller.texas.gov pages** (`tx_comptroller_valuing`, `tx_96_1569`, `tx_96_313`), a host whose robots file disallows `/*/`. They are in the held `impact_tax_rules` as the site file holds them. Default: kept, held; window D or the old laptop's forecast chain re-reads them from another host if you rule they must go.
- **Window 4's lost run files:** nothing to restore them from. Default: none; the next JEDI step downloads the workbooks again under its own ceiling.
