# Session 7515 report: Local impact (`/impact`) read as the reader it is for

Energy Research Warehouse (ERW), chain 304, part B (`queue/done/304-day-16-november-oldlaptop-done-line-economics.md`), samueloldlaptop, 16 November 2026. Branch `wip/7506-impact`, worktree `erw-7506`, on top of session 7506's head `946db9195`. Unattended. Model spend USD 0. Nothing pushed. The read: `docs/reviews/impact-read-2026-11-16.md`.

## At the top

- **One figure the page drew wrong is corrected (the one exception your rule for this page allows).** With Nevada's abatement on and a rate typed, the table by year's "Taxable value" showed 45 percent of the value in the abated years: USD 80.3 million in 2028 for Lone Mountain Geothermal, which the Department of Taxation's note values at USD 178,450,621, then a rise to USD 124.9 million in 2046 when the abatement ends. NRS 701A.370 abates "55 percent of the taxes", not the value. Now the column shows the whole value (USD 178.4 million in 2028, falling every year). **No tax, total or present value changed**: the tax beside it was already right (USD 876,642 against the Department's USD 876,653).
- **What the correction touched, more than the page's view:** the rule file `site/data/forecast/property_rules.json` (one field on Nevada's rule, `"abates": "tax"`; the file is written by hand, not by a builder), the model `site/lib/forecast.ts` (one line and the field's type), the trim `site/lib/forecastdata.ts`, the replication `replication/impact/replicate.py` (the same line, so the two implementations still agree) and one sentence of `docs/methods/forecast.md`, section 12.1. If you read the old column as a choice (the base the rate is applied to) and not as a wrong figure, undo commit `3baff8839`'s changes to these five files and drop the row's two tests (`site/scripts/test-impact-read.mjs`, the first two classes of `tests/test_session7515_impact_read.py`): the read's other 13 rows stand without it.
- **A consequence outside the site:** the builder of the warehouse table `impact_tax_rules` copies every field of a rule into `x_detail`, so at that table's next build one row gains the new field. Nothing was built here; it is the data request row below.
- **Everything else is a ruling, a browser read or that data row: 14 rows, 11 of them rulings, each with the default "unchanged".** The page's code is otherwise as session 7506 left it.
- **Not done:** no developer's or state's published claim was read for cases 2 to 5 (no request to any publisher was made this session); only Nevada's documents, which session 7506 read, are set beside the page. `docs/methods/economic_impact.md` and `docs/methods/impact_tax_rules.md` were not read line by line (the forecast note, its section 12, the faults file, the replication and the scripts were). The seller page's capacity factor was not compared (it states none; its hourly profile is in the live set). `check-values.mjs` was not run (it needs a served build).

## The reader and the five cases

- **The reader:** a state economic development office's analyst weighing an abatement (in Nevada, the Office of Energy's staff behind the Director's order). Every figure on the page is a state's (JEDI's multipliers, the statutes, OMB's discount rate), and A and B with the local option on and off is an abatement granted and refused. A county's own share, which a permitting lead needs, is nowhere on it.
- **1. Lone Mountain Geothermal**, Esmeralda County, Nevada, 36 MW, USD 178,446,043, order of 4 November 2026 (a state with an abatement): the tax by year is there once the county's rate is typed and agrees with the state's note; jobs are not in the order's units; row 1 was here.
- **2. Grant Solar**, McCook County, South Dakota, 99 MW, 2027 (no income tax): the fullest answer, USD 469,494 a year by statute; not said to whom.
- **3. Silver Queen Wind Farm**, Crawford County, Iowa, 252 MW, 2028 (the local levy not held): with the ordinance and a levy typed there is a figure; without the ordinance "not held", so the ordinance's cost cannot be read.
- **4. CPV Basin Ranch Energy Center**, Ward County, Texas, 1,445 MW of combined cycle, 2029 (gas with fuel): severance USD 13.7 million a year with Texas gas, where the case meets session 7511's rows 14 and 15 (cited, not rewritten); sales tax USD 61 million is an upper bound not said at the figure.
- **5. Cape Generating Station**, Beaver County, Utah, 86 MW, 2027, against the same plant in Nevada (A and B differ only by state): "Taxes, present value" USD 11.6 million against USD 0 is Utah's income tax alone, the figure of session 7506's row 4 (Utah's credit, not asked again); the state's default cost changes silently.

## The rows by kind (14)

- `site`: 1 (row 1, fixed with a test).
- `ruling`: 11 (rows 2 to 12).
- `data machine`: 1 (row 13).
- `browser`: 1 (row 14, four addresses).
- `license`, `key`: none.

## What was fixed

- Row 1 only, as "At the top" says. Commit `3baff8839`.

## Tests

Each file in its own process, `ERW_SPEND_CAP_USD=0`, `ERW_TABLES_DIR` the main copy's `warehouse/output` (read only), `.venv\Scripts\python.exe -m pytest tests/<file> -q`; the files found by grep for the changed modules.

| File | Result |
|---|---|
| `tests/test_session7515_impact_read.py` (new) | 7 passed (one runs `site/scripts/test-impact-read.mjs`, 10 of 10 on the drawn page; skipped without node or the table) |
| `tests/test_session7506_impact_replication.py` | 11 passed |
| `tests/test_session4203_forecast.py` (runs `site/scripts/test-forecast.test.mjs`) | 9 passed |
| `tests/test_session4219_forecast_faults.py` | 8 passed |
| `tests/test_session4221_forecast_readers.py` | 6 passed |
| `tests/test_session347.py` | 7 passed, 2 skipped |
| `tests/test_session412.py` | 20 passed |
| `node --import ./scripts/tsx-register.mjs scripts/impact-figures.mjs <table> --check` | exit 0: the 7,593 committed figures of 17 addresses are what the page draws after the change |
| `replication/impact/replicate.py --in-dir <tables>` | exit 0: `7593 of 7593 inside the tolerance` |

No site build, no full suite, no landing gate.

## What to review

In review (internal view). One page.

- `https://erw-flame.vercel.app/impact?tech=geothermal&state=nv&mw=36&cost=4956.83&start=2026&iaval=1&own=1.0917&ownyears=60&bmw=36&bcost=4956.83&bstart=2026&bown=1.0917&bownyears=60`
  - A and B: "Property tax, first operating year" USD 876,642 (A) and USD 1.9 million (B); "over the life" USD 36 million and USD 52.6 million; "Taxes, present value" USD 10.7 million and USD 19.7 million. Unchanged by this session.
  - Under "Scenario A by year", open "Every year". The column "Taxable value" should read USD 178.4 million in 2028, USD 127.9 million in 2045 and USD 124.9 million in 2046, falling every year (before: USD 80.3 million, USD 57.5 million, USD 124.9 million). "Property tax" beside it: USD 876,642 in 2028, USD 628,260 in 2045, USD 1.4 million in 2046, as before.
  - Click "Scenario B": the same "Taxable value" in every year.

## Data request rows

| Requested (UTC) | Session | Table or file | What, exactly | Source | State |
|---|---|---|---|---|---|
| 2026-11-16 12:50 | 7515 | `impact_tax_rules` (builder `warehouse/derived/impact_tax_rules.py`) | Once `wip/7506-impact` has landed: `site/data/forecast/property_rules.json` holds one new field on Nevada's rule (`"abates": "tax"`, rule `nv_renewable_abatement`). The builder copies a rule's fields into `x_detail`, so the row `erw_tax:nv:nv_renewable_abatement` changes at the table's next build and no other row should. Say built, and that one row differs | the rule file (NRS 701A.370, read 13 November 2026, request 105) | requested |

## Browser read rows

| Asked (UTC) | Session | Branch | Address | What to look at | What should be seen | State |
|---|---|---|---|---|---|---|
| 2026-11-16 12:50 | 7515 | wip/7506-impact | `https://erw-flame.vercel.app/impact?tech=geothermal&state=nv&mw=36&cost=4956.83&start=2026&iaval=1&own=1.0917&ownyears=60&bmw=36&bcost=4956.83&bstart=2026&bown=1.0917&bownyears=60` | "Every year" opened, at 1280 and at 390 px | Taxable value USD 178.4 million in 2028 and USD 124.9 million in 2046, lower every year; Property tax USD 876,642 in 2028; at 390 the table scrolls inside its own frame and the page does not | wanted |
| 2026-11-16 12:50 | 7515 | wip/7506-impact | the same address | hover the 2026 column of "Jobs by year", then of "Taxes by year" | "2026 (construction): 303 jobs (on site 130, supply chain 126, induced 46.8)"; "2026 (construction): property not held, sales none, income USD 0" (rows 2 and 6: the words as they stand) | wanted |
| 2026-11-16 12:50 | 7515 | wip/7506-impact | the same address | "Taxes, present value, in other states", hover Utah and Nevada | "Utah: USD 24.8 million (a property tax statute is held)"; "Nevada: USD 10.7 million (a property tax statute is held)" (row 8) | wanted |
| 2026-11-16 12:50 | 7515 | wip/7506-impact | `https://erw-flame.vercel.app/impact?tech=natural_gas&state=tx&mw=1445&start=2027&instate=100&bmw=1445&bstart=2027` | A and B; then open "Taxes" in the left box and hover "Sales tax exemption" | Severance, each year USD 13.7 million (A), "not held" (B); Sales and use tax USD 61 million in both; the hover says the figure is an upper bound before Texas's manufacturing exemption (row 9) | wanted |

## Landing request

- Head commit: the last commit of `wip/7506-impact` (the one that adds this report; its hash is in the session's reply). It stands on session 7506's stack, whose landing request is in `archive/sessions/SESSION_7506_REPORT.md`.
- Tests: the seven files above (68 passed, 2 skipped), the figures check and the replication.
- What changes for a visitor in the internal view: on `/impact`, the "Taxable value" column of the table by year for a Nevada wind, solar or geothermal plant with the local option on and a rate typed. No other cell of any address.
- Files: `site/lib/forecast.ts`, `site/lib/forecastdata.ts`, `site/data/forecast/property_rules.json`, `replication/impact/replicate.py`, `docs/methods/forecast.md`, new `site/scripts/impact-read.mjs`, `site/scripts/test-impact-read.mjs`, `tests/test_session7515_impact_read.py`, `docs/reviews/impact-read-2026-11-16.md`, this report.
- Pages a snapshot would differ on: none of the 25 (every page is in review). `check-values` should be run on the address above at the landing: the key `year:<yyyy>:value` is recomputed by the same library.

## Needs the key

None.

## Decisions made without you

- The reader is the state office's analyst, not the permitting lead, for the reason above; the five cases are four of session 7506's ten projects and Lone Mountain Geothermal.
- Row 1 was judged a wrong figure and not a choice: the column's name is "Taxable value", the rule file's own quote says the abatement is of the taxes, and the state's note prints the value. The field name `abates` and its one value `"tax"` are mine.
- The rule file was edited because it is hand-written from statutes (the note's opening), not written by a builder; the alternative, a rule's id named in the model's code, would have kept a statute's fact out of the file that holds the statutes.
- Case 3's levy (USD 30 per 1,000) is the value check's example figure, used to see what a click computes; it is not Crawford County's levy and the read says so. Case 4's in-state share (100 percent) is likewise the reader's input, not a fact about the plant.
- No publisher was asked for a claim for cases 2 to 5: the time went to the read. The read says so at its top.
- The reading script is committed as `site/scripts/impact-read.mjs` (not a scratch file), so the read can be drawn again; its text files are in `runs/7515/` (ignored).
- The seven test files were run one after another by one short script (`runs/7515/run_tests.sh`), each in its own process.

## For Samuel's ruling

Each in plain words; the default taken in every one is "the page stays as it is".

1. **On-site jobs are not in the A and B table** (row 2). The table shows the three effects added; a hearing and a developer's claim count workers at the site. Option: the on-site figure in the cell's hover or a row of its own.
2. **No tax figure says who receives it** (row 3). The state's and the local part of the sales tax are in the file the page reads and could be drawn apart; the property tax's receivers need each statute's sharing clause read.
3. **A and B do not say what differs, and there is no "B less A"** (row 4). Option: the head names the inputs not shared; a difference column.
4. **A new state in B silently brings that state's cost, rates and capacity factor** (row 5). Option: with ruling 3.
5. **The hover of "Taxes by year" uses "not held" and "none" in each other's place** (row 6).
6. **Nevada with no rate typed says "no rule held"** where a rule is held and a rate is missing (row 7).
7. **The reader's own county rate is carried to all 51 states in the taxes chart, and each hover then says "a property tax statute is held"** (row 8).
8. **A sales tax that is an upper bound does not say so at the figure** (row 9).
9. **Iowa: the levy typed does nothing without the ordinance**, so the ordinance's cost cannot be read from one county figure (row 10).
10. **`/impact` and the seller page give one wind plant two costs and two lives** (USD 1,482 per kW and 25 years from EIA; USD 2,100 and 30 from Lazard) (row 11). Default: each keeps its source.
11. **A figure above a million is written to a tenth of a million beside one written to the dollar** (row 12).
12. **Whether row 1 was a wrong figure or a choice** ("At the top"). Default taken: wrong, corrected.
